
all: usvd.ttl

usvd.ttl: usvd.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -c skosify.ini vocabulary.ttl usvd.tmp.ttl -o usvd.ttl

usvd.tmp.ttl: usvd.rdf.xml
	rapper -i rdfxml -o turtle usvd.rdf.xml >| usvd.tmp.ttl

usvd.rdf.xml: usvd.xml
	zorba -i convert.xq >| usvd.rdf.xml

#usvd.xml:
#	<eksporteres ikke automatisk fra bibsys enda>
#    wget -nv -O usvd.xml http://www.bibsys.no/files/out/humordsok/USVDregister.xml

clean:
	rm -f usvd.rdf.xml
	rm -f usvd.ttl
	rm -f usvd.tmp.ttl
