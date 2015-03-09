# encoding=utf8
"""
Dette er et script for å gå gjennom BIBSYSMARC-kildefilene i 'src'-mappen
og konvertere til objekter på formen

    {
         'id': '<objekt-id>',
         'classes':[
             {'notation': '530.12', 'system': 'ddc', 'edition': 'DDC-23', 'assigner': 'k'},
             {'notation': '530.14', 'system': 'ddc', 'edition': None, 'assigner': 'k'}
         ],
         'subjects':[
             {'term': 'Kvantemekanikk', 'vocab': 'no-ubo-mn', 'assigner': 'k'},
             {'term': 'Kvantemekanikk', 'vocab': 'humord', 'assigner': 'k'}
         ]
    }

Nederst finnes noen funksjoner som trekker ut litt statistikk.

Merk at strengtermer omgjøres til kolonseparerte strenger. Dette passer bra for
prekoordinerte vokabualer. Eksempelvis blir "$a Boligområder $b Regulering" til
"Boligområder : Regulering". I vokabularer der $b som kvalifikator bør strengformen
omgjøres til å bruke parentes, noe som enkelt kan gjøres med regexp.

"""
import sys
import re
from glob import glob
import codecs
import logging
import logging.handlers
import h5py
import numpy as np


class Document(object):
    """
    Eksempel:

        >>> doc = Document('101478674')
        >>> doc.add_class('ddc', 'DDK-23', '781.599', 'k')
        >>> doc.add_class('ddc', 'DDK-23', '355.1', 'k')
        >>> doc.add_subject('humord', 'Trommer', 'd')
        >>> doc.add_subject('humord', 'Blåseinstrumenter', 'd')
        >>> doc.add_subject('humord', 'Militærvesen', 'd')
        >>> doc.serialize()
    """

    def __init__(self, id):
        self.id = id
        self.classes = []
        self.subjects = []

    def get_class(self, system, notation, assigner):
        for c in self.classes:
            if c['system'] == system and c['notation'] == notation and c['assigner'] == assigner:
                return c

    def get_subject(self, vocab, term, assigner):
        for c in self.subjects:
            if c['vocab'] == vocab and c['term'] == term and c['assigner'] == assigner:
                return c

    def add_class(self, system, edition, notation, assigner):
        if system == 'ddc':
            m = re.match('([0-9]+(?:\.[0-9]*)?)', notation)
            if m is None:
                logging.warn('Invalid DDC: "%s"', notation)
            elif m.group() != notation:
                logging.info('DDC: Normalizing "%s" as "%s"', notation, m.group())
                notation = m.group()

        c = self.get_class(system, notation, assigner)
        if c is not None:
            if edition is not None:
                c['edition'] = edition
                # logging.info('Prefer editioned class over non-editioned: %s %s %s %s %s', self.id, system, edition, notation, assigner)
            return
        self.classes.append({
            'notation': notation,
            'assigner': assigner,
            'system': system,
            'edition': edition
        })

    def add_subject(self, term, assigner, vocab):
        c = self.get_subject(vocab, term, assigner)
        if c is not None:
            # logging.info('Ignore dup: %s %s %s %s', self.id, vocab, term, assigner)
            return
        self.subjects.append({
            'term': term,
            'assigner': assigner,
            'vocab': vocab
        })

    def serialize(self):
        return {'id': self.id, 'subjects': self.subjects, 'classes': self.classes}


class BsExtrator(object):
    """
    Iterate over document records in a list of files.

    Example:

        >>> ex = BsExtrator(['src/out2011.mrc', 'src/out2012.mrc', 'src/out2013.mrc'])
        >>> for record in ex.records():
        >>>    if len(record['classes']) != 0 or len(record['subjects']) != 0:
        >>>        print(record['id'])
        >>>        for c in record['classes']:
        >>>            print(u'- {} (Vocabulary: {} Edition: {} Assigner: {})'.format(c.get('notation'),
        ...                  c.get('system'), c.get('edition'), c.get('assigner')).encode('utf8'))
        >>>        for c in record['subjects']:
        >>>            print(u'- {} (Vocabulary: {} Assigner: {})'.format(c.get('term'), c.get('vocab'),
        ...                  c.get('assigner')).encode('utf8'))

    """
    def __init__(self, files):
        self.files = files

    def lag_streng(self, sf):
        # Lager en emneordsstreng av delfeltene i MARC-feltet
        # Hvert delfelt kan repeteres
        streng = []
        for q in ['a', 'b']:
            if q in sf:
                for p in sf[q]:
                    streng.append(p)
        return ' : '.join(streng)

    def process_object(self, obj):
        # Behandling av emneord og klassifikasjon for ett objekt (én MARC-post)
        o = Document(obj['id'])
        for field in obj['fields']:

            # Kontrollert emneord (687)
            if field['code'] == '687' and 'assigner' in field and '2' in field['subfields']:
                o.add_subject(
                    term=self.lag_streng(field['subfields']),
                    assigner=field['assigner'],
                    vocab=field['subfields']['2'][0]
                )

            # Tekord (699)
            if field['code'] == '699' and 'assigner' in field:
                o.add_subject(
                    term=self.lag_streng(field['subfields']),
                    assigner=field['assigner'],
                    vocab='tekord'
                )

            # Mesh (660)
            if field['code'] == '660' and 'assigner' in field:
                o.add_subject(
                    term=self.lag_streng(field['subfields']),
                    assigner=field['assigner'],
                    vocab='mesh'
                )

            # Agrovoc (670)
            if field['code'] == '670' and 'assigner' in field:
                o.add_subject(
                    term=self.lag_streng(field['subfields']),
                    assigner=field['assigner'],
                    vocab='agrovoc'
                )

            # Humord (698)
            if field['code'] == '698' and 'assigner' in field:
                o.add_subject(
                    term=self.lag_streng(field['subfields']),
                    assigner=field['assigner'],
                    vocab='humord'
                )

            # Dewey (082)
            if field['code'] == '082' and 'assigner' in field:

                # $a Hovednummer
                if 'a' in field['subfields']:
                    for notation in field['subfields']['a']:
                        o.add_class(
                            system='ddc',
                            edition=field['subfields']['2'][0] if '2' in field['subfields'] else None,
                            notation=notation,
                            assigner=field['assigner']
                        )

                # $a Alternativt nummer
                if 'b' in field['subfields']:
                    for notation in field['subfields']['b']:
                        o.add_class(
                            notation=notation,
                            assigner=field['assigner'],
                            system='ddc',
                            edition=field['subfields']['2'][0] if '2' in field['subfields'] else None
                        )

                # $d (R)DEWEY-nummer fra NB (Nasjonalbiblioteket)
                if 'd' in field['subfields']:
                    for notation in field['subfields']['d']:
                        o.add_class(
                            notation=notation,
                            assigner='g',  # NB
                            system='ddc',
                            edition=field['subfields']['2'][0] if '2' in field['subfields'] else None
                        )

        return o.serialize()

    def add_field(self, obj, field):
        if field is not None and len(field['subfields']) != 0:
            obj['fields'].append(field)

        return obj, field

    def records(self):

        for fname in self.files:
            logging.info('Read: %s' % (fname))
            f = codecs.open(fname, 'r', 'latin1')
            lines = [x.strip() for x in f.readlines()]

            obj = {'fields': []}
            field = None
            for linenum, line in enumerate(lines):

                # Start of new field
                if line[0] == '*':
                    obj, field = self.add_field(obj, field)
                    field = {'subfields': {}}
                    field['code'] = line[1:4]
                    if field['code'] == '000':
                        l = line.split()
                        objektid = l[1]
                        obj['id'] = objektid
                    else:
                        bibkode = line[4:6].strip()
                        field['assigner'] = bibkode

                # Start of new object/post
                elif line[0] == '^':
                    obj, field = self.add_field(obj, field)
                    field = None
                    obj = self.process_object(obj)
                    if obj is not None:
                        yield obj
                    obj = {'fields': []}

                if len(line) > 0 and line[0] == '$' or len(line) > 6 and line[6] == '$':
                    try:
                        feltkode = line[line.find('$') + 1]
                        rest = line[line.find('$') + 2:]
                        if feltkode not in field['subfields']:
                            field['subfields'][feltkode] = []
                        field['subfields'][feltkode].append(rest)
                    except:
                        logging.error('Error at %s, line %d', fname, linenum)
                        sys.exit(1)


def get_humord_real_ddc(cat_files):
    """
    Henter ut bare Humord, Realfagstermer og DDC, som returneres som hver sin liste.
    """

    ddc = []
    hume = []
    real = []

    # Loop over bibliographic records
    ex = BsExtrator(cat_files)
    for record in ex.records():

        id = record['id']
        year = int(id[0:2])
        if year < 50:
            year = 2000 + year
        else:
            year = 1900 + year

        for field in record['classes']:

            if field.get('system') == 'ddc':
                ddc.append([year, id, field.get('notation'), field.get('edition'), field.get('assigner')])

        for field in record['subjects']:

            if field.get('vocab') == 'humord':
                term = field.get('term')

                # Endre fra streng til formen 'Hovedterm (Kvalifikator)' som brukes i Humord:
                m = re.match('^(.*?) : (.*)$', term)
                if m:
                    term = '%s (%s)' % (m.groups()[0], m.groups()[1])

                hume.append([year, id, term, field.get('assigner')])

            if field.get('vocab') == 'no-ubo-mn':
                real.append([year, id, field.get('term'), field.get('assigner')])

    return ddc, hume, real


def count_editions(ddc):
    """
    Teller opp hvor mange DDC vi har med ulike DDC-utgaver, både for UBO og nasjonalt.
    """
    editions = set(map(lambda x: x[3], ddc))
    usage = []
    for ed in editions:
        q = filter(lambda x: x[3] == ed, ddc)
        q2 = filter(lambda x: x[4] == 'k', q)
        usage.append([ed, len(q), len(q2)])
    usage = filter(lambda x: x[1] > 100, usage)
    usage = sorted(usage, lambda a, b: cmp(a[1], b[1]), reverse=True)
    print usage


def get_common_ids(voc1, voc2):
    # Returns a set of IDs common to voc1 and voc2
    ids1 = set(map(lambda x: x[1], voc1))
    ids2 = set(map(lambda x: x[1], voc2))
    common_ids = ids1.intersection(ids2)
    return common_ids


def filter_docs(ddc, hume, rt, lim=2000):
    """
    Teller opp hvor mange dokumenter vi har med både DDC og Humord/Realfagsterm
    avhengig av hvilke avgrensninger vi setter.
    """

    print 'Ingen avgrensning:'
    print '(ddc, hume):', len(get_common_ids(ddc, hume))
    print '(ddc, real):', len(get_common_ids(ddc, rt))

    print 'Alternativ 1 - Avgrense til DDC-23:'
    ddc_r1 = [x for x in ddc if x[3] == 'DDC-23']  # and x[4] in ['k', 'd', 'xt', 'a']]
    print '(ddc, hume):', len(get_common_ids(ddc_r1, hume))
    print '(ddc, real):', len(get_common_ids(ddc_r1, rt))

    print 'Alternativ 2 - Avgrense til DDC-23 og >= 2012: (som gjort i Realfagsterm-prosjektet)'
    ddc_r2 = [x for x in ddc_r1 if x[0] >= 2012]  # and x[4] in ['k', 'd', 'xt', 'a']]
    print '(ddc, hume):', len(get_common_ids(ddc_r2, hume))
    print '(ddc, real):', len(get_common_ids(ddc_r2, rt))

    print 'Alternativ 3 - Avgrense til >= 2000:'
    ddc_r3 = [x for x in ddc if x[0] >= lim]  # and x[4] in ['k', 'd', 'xt', 'a']]
    hume_r = [x for x in hume if x[0] >= lim]
    rt_r = [x for x in rt if x[0] >= lim]
    print '(ddc, hume):', len(get_common_ids(ddc_r3, hume_r))
    print '(ddc, rt):', len(get_common_ids(ddc_r3, rt_r))

    print 'Alternativ 3 - Avgrense til >= 2000 og DDC fra Humord-bibl: (mest aktuelt for Humord-prosjektet?)'
    ddc_r4 = [x for x in ddc_r3 if x[4] in ['k', 'd', 'xt', 'a']]
    print '(ddc, hume):', len(get_common_ids(ddc_r4, hume_r))
    print '(ddc, rt):', len(get_common_ids(ddc_r4, rt_r))

    return get_common_ids(ddc_r4, hume_r), get_common_ids(ddc_r4, rt_r)


def remove_dups(voc):
    # 1) Remove x[3:] (edition and assigner) for x in voc.
    # 2) Remove duplicates
    q = set([':'.join(x[1:3]) for x in voc])
    return [x.split(':', 1) for x in q]


def make_pair_list(voc1, voc2, ids):
    """
    vocX: (n,m) array where
        vocX(n,0) = document id
        vocX(n,1) = term / notation
    ids: flat list of document ids
    """

    # At this point we are no longer interested in edition and assigner.
    # Let's simplify and remove dups
    voc1 = remove_dups([x for x in voc1 if x[1] in ids])
    voc2 = remove_dups([x for x in voc2 if x[1] in ids])

    docs = {}
    for row in voc1:
        id = row[0]
        if id not in docs:
            docs[id] = {'alpha': [], 'beta': []}
        docs[id]['alpha'].append(row[1])

    for row in voc2:
        id = row[0]
        if id not in docs:
            docs[id] = {'alpha': [], 'beta': []}
        docs[id]['beta'].append(row[1])

    # Make a list of all pairs
    pairs = []
    for doc in docs.values():
        for a in doc['alpha']:
            for b in doc['beta']:
                pairs.append([a, b])

    return np.array(pairs)


def pair_list_to_hdf5(fname, pairs):
    # pairs is a (n,2) numpy array
    h5f = h5py.File(fname, 'w')
    pairs = np.char.encode(pairs, 'utf-8')
    h5f.create_dataset('pairs', data=pairs)


if __name__ == '__main__':
    ddc, hume, real = get_humord_real_ddc(glob('src/*.mrc'))

    hume_ddc_ids, real_ddc_ids = filter_docs(ddc, hume, real, 2000)

    hume_ddc = make_pair_list(hume, ddc, hume_ddc_ids)
    real_ddc = make_pair_list(real, ddc, real_ddc_ids)

    pair_list_to_hdf5('hume_ddc.hdf5', hume_ddc)
    pair_list_to_hdf5('real_ddc.hdf5', real_ddc)
