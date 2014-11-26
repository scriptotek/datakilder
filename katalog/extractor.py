# encoding=utf8

import sys
import re
import codecs
import logging
import logging.handlers


class BsExtrator:

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
        o = {'id': obj['id'], 'subjects': [], 'classes': []}
        for field in obj['fields']:

            # Kontrollert emneord (687)
            if field['code'] == '687' and 'assigner' in field and '2' in field['subfields']:
                o['subjects'].append({
                    'term': self.lag_streng(field['subfields']),
                    'assigner': field['assigner'],
                    'vocab': field['subfields']['2'][0]
                })

            # Tekord (699)
            if field['code'] == '699' and 'assigner' in field:
                o['subjects'].append({
                    'term': self.lag_streng(field['subfields']),
                    'assigner': field['assigner'],
                    'vocab': 'tekord'
                })

            # Mesh (660)
            if field['code'] == '660' and 'assigner' in field:
                o['subjects'].append({
                    'term': self.lag_streng(field['subfields']),
                    'assigner': field['assigner'],
                    'vocab': 'mesh'
                })

            # Agrovoc (670)
            if field['code'] == '670' and 'assigner' in field:
                o['subjects'].append({
                    'term': self.lag_streng(field['subfields']),
                    'assigner': field['assigner'],
                    'vocab': 'agrovoc'
                })

            # Humord (698)
            if field['code'] == '698' and 'assigner' in field:
                o['subjects'].append({
                    'term': self.lag_streng(field['subfields']),
                    'assigner': field['assigner'],
                    'vocab': 'humord'
                })

            # Dewey (082)
            if field['code'] == '082' and 'assigner' in field:
                o['classes'].append({
                    'notation': field['subfields']['a'] if 'a' in field['subfields'] else [],
                    'assigner': field['assigner'],
                    'system': 'ddc',
                    'edition': field['subfields']['2'][0] if '2' in field['subfields'] else None
                })

        return o

    def add_field(self, obj, field):
        if field is not None and len(field['subfields']) != 0:
            obj['fields'].append(field)

        return obj, field

    def __init__(self):
        pass

    def process(self, files):
        # Process a list of files

        for fname in files:
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
