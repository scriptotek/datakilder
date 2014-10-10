
all: USVDregister.ttl

USVDregister.ttl: USVDregister.rdf.xml
	rapper -i rdfxml -o turtle USVDregister.rdf.xml >| USVDregister.ttl

USVDregister.rdf.xml: USVDregister.xml
	zorba -i convert.xq >| USVDregister.rdf.xml

#USVDregister.xml:
#	<eksporteres ikke automatisk fra bibsys enda>
#    wget http://www.bibsys.no/files/out/humordsok/USVDregister.xml

clean:
	rm USVDregister.rdf.xml
	rm USVDregister.ttl
