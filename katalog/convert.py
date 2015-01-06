# encoding=utf8
#
# Dette scriptet leser `*.mrc`-filene i `./src/` og skriver ut RDF til
# `bib.ttl`.  Se README.md for mer info om konverteringsprosessen.
#
# Alle HUMORD-innførsler sjekkes mot den oppdaterte RDF-representasjon av
# autoritetsregisteret som leses fra `HUMEregister.ttl`. I tilfeller der
# emneordet ikke blir funnet, lagres objektid til filen `vaskeliste.json`
# for videre behandling med scriptet `vaskeliste.py`.

import re
import sys
import logging
import logging.handlers
from extractor import BsExtrator
import argparse
import json
from rdflib.namespace import Namespace, RDF, RDFS, SKOS, DCTERMS
from rdflib import URIRef, RDFS, Literal, Graph

DEWEY = Namespace('http://dewey.info/schema-terms/')
UBO = Namespace('http://data.ub.uio.info/elements#')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

schemes = {
    'ddc23': {'ns': Namespace('http://dewey.info/class/'), 'el': '{id}/e23/'},
    'bib': {'ns': Namespace('http://data.ub.uio.no/bib/'), 'el': 'c{id}'}
}


def uri(scheme, id):
    scheme = schemes[scheme]
    return scheme['ns'][scheme['el'].format(id=id)]


def extract(humord_file, cat_files):

    # Mapping fra BIBSYS-tegnsett til unicode
    charmap = {
        u'@æ': u'ä',
        u'@Æ': u'Ä',
        u'@ø': u'ö',
        u'@Ø': u'Ö',
        u'@y': u'ü',
        u'@Y': u'Ü',
        u'@i': u'ı',
        u'#ug': u'ğ',
    }

    # Documents with subject headings that could not be matched
    documentsToCheck = []

    logger.info('Load: %s' % (humord_file))

    # Load humord
    humord = Graph()
    humord.load(humord_file, format='turtle')

    # Create a new graph for our output
    out = Graph()
    dct = Namespace('http://purl.org/dc/terms/')
    nm = out.namespace_manager
    nm.bind('dct', 'http://purl.org/dc/terms/')
    nm.bind('skos', SKOS)

    # Add a concept scheme
    scheme = URIRef('http://data.ub.uio.no/bib/')
    out.add((scheme, RDF.type, SKOS.ConceptScheme))

    # Loop over bibliographic records
    ex = BsExtrator()
    for record in ex.process(cat_files):

        concept = uri('bib', record['id'])

        for field in record['classes']:

            # Assigner: UBO (k), edition: DDC-23
            if field.get('system') == 'ddc':

                if field.get('edition') == 'DDC-23' and field.get('assigner') == 'k':
                    for x in field.get('notation'):  # list
                        m = re.match('^([^0-9.]*?)([0-9.]+)(.*?)$', x)
                        val = uri('ddc23', m.groups()[1])
                        out.add((concept, DCTERMS.subject, val))
                        if (len(m.groups()[0]) != 0 or len(m.groups()[2]) != 0):
                            logger.error('Dok %s - DDK23 inneholder uventede tegn: %s' % (record['id'], x))

        for field in record['subjects']:

            # Assigner: UBO (k), vocabulary: 'humord'
            if field.get('vocab') == 'humord' and field.get('assigner') == 'k':

                term = field.get('term')

                # Endre fra streng til formen 'Hovedterm (Kvalifikator)' som brukes i Humord:
                m = re.match('^(.*?) : (.*)$', term)
                if m:
                    term = '%s (%s)' % (m.groups()[0], m.groups()[1])

                if re.search(u' \((Form|Ordbøker)\)', term):  # Case-sensitive
                    # Disse ligger nå i 655.
                    # Denne sjekken kan droppes når vi får oppdaterte katalogdata
                    continue

                # Konvertér fra BIBSYS-tegnsett
                for s, t in charmap.items():
                    term = term.replace(s, t)

                # Slå opp i humord for å finne URIen:
                try:
                    val = humord.triples((None, SKOS.prefLabel, Literal(term, lang='nb'))).next()
                    out.add((concept, DCTERMS.subject, val[0]))
                except StopIteration:
                    try:
                        val = humord.triples((None, SKOS.altLabel, Literal(term, lang='nb'))).next()
                        out.add((concept, DCTERMS.subject, val[0]))
                    except StopIteration:
                        logger.error('Dok %s - Fant ikke i Humord: %s' % (record['id'], term))
                        documentsToCheck.append(record['id'])

        if len([x for x in out.predicate_objects(concept)]) != 0:
            year = 1900 + int(record['id'][:2])
            if year < 1960:
                year += 100
            out.add((concept, RDF.type, DCTERMS.BibliographicResource))
            out.add((concept, DCTERMS.date, Literal('{}'.format(year))))

    return out, documentsToCheck


def main():
    out, documentsToCheck = extract('../humord/HUMEregister.ttl', ['src/out%d.mrc' % year for year in range(1974, 2015)])

    logger.info('Write: vaskeliste.json')
    json.dump(documentsToCheck, open('vaskeliste.json', 'w'))

    logger.info('Write: bib.ttl')
    out.serialize('bib.ttl', format='turtle')


main()
