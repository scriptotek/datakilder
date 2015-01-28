
all: USVDregister.ttl

USVDregister.ttl: USVDregister.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -c skosify.ini vocabulary.ttl USVDregister.tmp.ttl -o USVDregister.ttl

USVDregister.tmp.ttl: USVDregister.rdf.xml
	rapper -i rdfxml -o turtle USVDregister.rdf.xml >| USVDregister.tmp.ttl

USVDregister.rdf.xml: USVDregister.xml
	zorba -i convert.xq >| USVDregister.rdf.xml

#USVDregister.xml:
#	<eksporteres ikke automatisk fra bibsys enda>
#    wget http://www.bibsys.no/files/out/humordsok/USVDregister.xml

clean:
	rm -f USVDregister.rdf.xml
	rm -f USVDregister.ttl
	rm -f USVDregister.tmp.ttl
