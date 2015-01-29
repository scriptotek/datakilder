# encoding=utf8
#
# Dette scriptet verifiserer Humord-innførslene for en liste dokumenter
# hentet fra `vask.json`. For hvert dokument hentes oppdaterte emneinnførsler
# fra Bibsys' SRU-tjeneste via KatApi, og disse blir sjekket mot oppdaterte
# autoritetsdata fra `humord.ttl`. Feilinnførsler lagres til filen
# `humord-vask.xlsx`.

import requests
import json
from rdflib.namespace import Namespace, RDF, RDFS, SKOS, DCTERMS
from rdflib import URIRef, RDFS, Literal, Graph
import logging
import logging.handlers
import codecs
import re
import time
import xlsxwriter

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('humord-vask.xlsx')
worksheet = workbook.add_worksheet()

bold = workbook.add_format({'bold': True})
worksheet.write('A1', u'Status', bold)
worksheet.write('B1', u'Objekt-ID', bold)
worksheet.write('C1', u'Nåværende $a', bold)
worksheet.write('D1', u'Nåværende $b', bold)
worksheet.write('E1', u'Ny $a', bold)
worksheet.write('F1', u'Ny $b', bold)

logger = logging.getLogger('vask')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

humord_file = '../humord/humord.ttl'
logger.info('Load: %s' % (humord_file))
humord = Graph()
humord.load(humord_file, format='turtle')

ids = json.load(open('vaskeliste.json', 'r'))


def in_register(term):
    try:
        val = humord.triples((None, SKOS.prefLabel, Literal(term, lang='nb'))).next()
        return True
    except StopIteration:
        try:
            val = humord.triples((None, SKOS.altLabel, Literal(term, lang='nb'))).next()
            return True
        except StopIteration:
            return False


def get_doc(id):
    try:
        return json.loads(requests.get('http://katapi.biblionaut.net/documents/show/{}.json'.format(id)).text)
    except:
        logger.error('Failed. Retrying in 10 secs')
        time.sleep(10)
        return get_doc(id)


line = 0
for id in ids:
    doc = get_doc(id)

    status = '(ukjent)'
    for holding in doc.get('holdings', []):
        if holding['location'] == 'UBO':
            status = holding['status']

    if 'error' in doc:
        logger.error('Document could not be parsed. Continuing')
        continue

    terms = [x['indexTerm'] for x in doc['subjects'] if x['vocabulary'] == 'humord']
    # logger.info('%s : %s', id, ', '.join(terms))
    for term in terms:
        if not in_register(term):
            # logger.error('Dok %s - Fant ikke i Humord: %s' % (id, term))
            a, b = (term, '')
            m = re.match('^(.*?) \((.*)\)$', term)
            if m:
                a, b = (m.group(1), m.group(2))

            a2 = ''
            b2 = ''

            af = a[0].upper() + a[1:]
            bf = ''
            x = af
            if len(b) > 1:
                bf = b[0].upper() + b[1:]
                x += u' (%s)' % (bf,)

            if in_register(x):
                a2 = af
                b2 = bf
            elif in_register(af):
                a2 = af
                b2 = ''

            line += 1
            worksheet.write(line, 0, status)
            worksheet.write(line, 1, id)
            worksheet.write(line, 2, a)
            worksheet.write(line, 3, b)
            worksheet.write(line, 4, a2)
            worksheet.write(line, 5, b2)

            logger.info(u'{:>10} {:<50} {:<50} {:<50} {:<50}'.format(id, a, b, a2, b2))

    time.sleep(3)  # give Bibsys some rest

workbook.close()
