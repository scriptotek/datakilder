#!/usr/bin/env python
# encoding=utf-8
"""
 Usage:
    Use the same way as you would use skosify

 Example:
    ./skosify-sort.py -b 'http://data.ub.uio.no/' -o humord.ttl vocabulary.ttl humord.tmp.ttl
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import re
import sys
import argparse
from rdflib import Graph, BNode
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib.namespace import RDF, RDFS, SKOS, FOAF, Namespace

try:
    from skosify import Skosify
except:
    print('Please install skosify first')
    sys.exit(1)


class OrderedTurtleSerializer(TurtleSerializer):

    short_name = "turtle"

    def __init__(self, store):
        super(OrderedTurtleSerializer, self).__init__(store)

        SD = Namespace('http://www.w3.org/ns/sparql-service-description#')
        ISOTHES = Namespace('http://purl.org/iso25964/skos-thes#')

        # Order of classes:
        self.topClasses = [SKOS.ConceptScheme,
                           FOAF.Organization,
                           SD.Service,
                           SD.Dataset,
                           SD.Graph,
                           SD.NamedGraph,
                           ISOTHES.ThesaurusArray,
                           SKOS.Concept]

        # Order of instances:
        def compare(x, y):
            x2 = int(re.sub(r'[^0-9]', '', x))
            y2 = int(re.sub(r'[^0-9]', '', y))
            if x2 == 0 or y2 == 0:
                return cmp(x, y)
            else:
                return cmp(x2, y2)

        self.sortFunction = compare

    def orderSubjects(self):
        seen = {}
        subjects = []

        for classURI in self.topClasses:
            members = list(self.store.subjects(RDF.type, classURI))
            members.sort(self.sortFunction)

            for member in members:
                subjects.append(member)
                self._topLevels[member] = True
                seen[member] = True

        recursable = [
            (isinstance(subject, BNode),
             self._references[subject], subject)
            for subject in self._subjects if subject not in seen]

        recursable.sort()
        subjects.extend([subject for (isbnode, refs, subject) in recursable])

        return subjects


def skosify_process(voc):

    # logging.info("Performing inferences")

    skosify = Skosify()

    # Perform RDFS subclass inference.
    # Mark all resources with a subclass type with the upper class.
    # skosify.infer_classes(voc)
    # skosify.infer_properties(voc)

    # logging.info("Setting up namespaces")
    # skosify.setup_namespaces(voc, namespaces)

    # logging.info("Phase 4: Transforming concepts, literals and relations")

    # special transforms for labels: whitespace, prefLabel vs altLabel
    # skosify.transform_labels(voc, options.default_language)

    # special transforms for collections + aggregate and deprecated concepts
    # skosify.transform_collections(voc)

    # find concept schema and update date modified
    cs = skosify.get_concept_scheme(voc)
    skosify.initialize_concept_scheme(voc, cs,
                                      label=False,
                                      language='nb',
                                      set_modified=True)

    # skosify.transform_aggregate_concepts(voc, cs, relationmap, options.aggregates)
    # skosify.transform_deprecated_concepts(voc, cs)

    # logging.info("Phase 5: Performing SKOS enrichments")

    # Enrichments: broader <-> narrower, related <-> related
    # skosify.enrich_relations(voc, options.enrich_mappings,
    #                  options.narrower, options.transitive)

    # logging.info("Phase 6: Cleaning up")

    # Clean up unused/unnecessary class/property definitions and unreachable
    # triples
    # if options.cleanup_properties:
    #     skosify.cleanup_properties(voc)
    # if options.cleanup_classes:
    #     skosify.cleanup_classes(voc)
    # if options.cleanup_unreachable:
    #     skosify.cleanup_unreachable(voc)

    # logging.info("Phase 7: Setting up concept schemes and top concepts")

    # setup inScheme and hasTopConcept
    # skosify.setup_concept_scheme(voc, cs)
    # skosify.setup_top_concepts(voc, options.mark_top_concepts)

    # logging.info("Phase 8: Checking concept hierarchy")

    # check hierarchy for cycles
    skosify.check_hierarchy(voc, break_cycles=True, keep_related=False,
                            mark_top_concepts=False, eliminate_redundancy=True)

    # logging.info("Phase 9: Checking labels")

    # check for duplicate labels
    # skosify.check_labels(voc, options.preflabel_policy)


class SkosifySorted(Skosify):
    """ Modified Skosify class to write sorted Turtle output """

    def write_output(self, rdf, filename, fmt):
        """Serialize the RDF output to the given file (or - for stdout)."""
        if filename == '-':
            out = sys.stdout
        else:
            out = open(filename, 'wb')

        # logging.debug("Writing output file %s (format: %s)", filename, fmt)
        s = OrderedTurtleSerializer(rdf)
        s.serialize(out, base=base)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='RDF postprocessor')
    parser.add_argument('infiles', nargs='*', help='Input Turtle files')
    parser.add_argument('-b', '--base', dest='base', help='Base prefix')
    parser.add_argument('-o', '--outfile', dest='outfile', help='Destination file')
    args = parser.parse_args()

    # parser.add_argument('outfile', nargs=1, help='Output RDF file')
    # parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='More verbose output')
    # parser.add_argument('-o', '--outformat', dest='outformat', nargs='?',
    #                     help='Output serialization format. Any format supported by rdflib. Default: turtle',
    #                     default='turtle')

    g = Graph()
    args = parser.parse_args()
    formats = {'.ttl': 'turtle', '.nt': 'nt'}
    for fname in args.infiles:
        ff = formats[os.path.splitext(fname)[-1]]
        g.load(fname, format=ff)

    skosify_process(g)

    s = OrderedTurtleSerializer(g)
    fobj = open(args.outfile, 'w')
    if args.base:
        fobj.write('@base <http://data.ub.uio.no/> .\n')
        s.serialize(fobj, base=args.base)
    else:
        s.serialize(fobj)
