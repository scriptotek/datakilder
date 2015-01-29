#!/usr/bin/env python
# encoding=utf-8
"""
 Usage:
    Use the same way as you would use skosify

 Example:
    ./skosify-sort.py -c skosify.ini vocabulary.ttl humord.tmp.ttl -o humord.ttl
"""
from __future__ import absolute_import
from __future__ import print_function

import re
import sys
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib.namespace import RDF, RDFS, SKOS
try:
    from skosify import Skosify
except:
    print('Please install skosify first')
    sys.exit(1)


class OrderedTurtleSerializer(TurtleSerializer):

    short_name = "turtle"

    def __init__(self, store):
        super(OrderedTurtleSerializer, self).__init__(store)

        # Order of classes:
        self.topClasses = [SKOS.ConceptScheme, SKOS.Concept]

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


class SkosifySorted(Skosify):
    """ Modified Skosify class to write sorted Turtle output """

    def __init__(self):
        super(SkosifySorted, self).__init__()

    def write_output(self, rdf, filename, fmt):
        """Serialize the RDF output to the given file (or - for stdout)."""
        if filename == '-':
            out = sys.stdout
        else:
            out = open(filename, 'wb')

        # logging.debug("Writing output file %s (format: %s)", filename, fmt)
        s = OrderedTurtleSerializer(rdf)
        s.serialize(out)


if __name__ == '__main__':
    skosify = SkosifySorted()
    skosify.main()
