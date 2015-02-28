
all: tekord.ttl

tekord.ttl: tekord.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -b 'http://data.ub.uio.no/' -o tekord.ttl vocabulary.ttl tekord.tmp.ttl
	rm -f tekord.tmp.ttl

tekord.tmp.ttl: tekord.rdf.xml
	rapper -i rdfxml -o turtle tekord.rdf.xml >| tekord.tmp.ttl

tekord.rdf.xml: tekord.xml
	zorba -i convert.xq >| tekord.rdf.xml

# tekord.xml:
#	<eksporteres ikke automatisk fra bibsys enda>

clean:
	rm -f tekord.rdf.xml
	rm -f tekord.ttl
	rm -f tekord.tmp.ttl
