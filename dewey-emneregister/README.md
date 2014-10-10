## UBOs emneregister til Dewey

### Innhold

Universitetsbiblioteket i Oslos emneregister til Dewey, også kjent
som UBOs kjederegister til Dewey, tidligere kjent som UBO/SV's kjederegister
til Dewey, derav akronymet USVD som fremdeles brukes.

Registeret er søkbart på <http://wgate.bibsys.no/search/pub?base=USVDEMNE>.
Det vedlikeholdes i BIBSYS' emnemodul, og vi har fått en XML-eksport
derfra (`USVDregister.xml`) på epost fra Gunvald 30. juni 2014.

* `USVDregister.xml` : Registeret som eksportert fra BIBSYS' emnemodul.
* `USVDregister.ttl` : Registeret konvertert til RDF og serialisert som Turtle.
* `convert.xq` : XQuery-script for å konvertere `USVDregister.xml` til RDF.

### Konverteringsprosessen

I registerfilen er hver term angitt som et `<post>`-element. Dette har
underelementer som `<term-id>`, `<hovedemnefrase>`, osv. Under vises
vår foreløpige modell for mapping av disse elementene til RDF, som
implementert i `convert.xq`. Vi bruker hovedsakelig
[SKOS-vokabularet](http://www.w3.org/2004/02/skos/core.html).

    if <se-id> then

      <http://data.ub.uio.no/usvd/<se-id> a skos:Concept
        skos:altLabel "<hovedemnefrase> (<kvalifikator>)"@nb

    else:

      <http://data.ub.uio.no/usvd/<term-id> a skos:Concept
        skos:prefLabel "<hovedemnefrase> : <kjede>"@nb
        dcterms:identifier "<term-id>"
        dcterms:date "<dato>"^^xs:date
        skos:notation "<signatur>"^^<http://dewey.info/schema-terms/Notation>
        skos:definition "<definisjon>"@nb
        skos:editorialNote "<noter>"@nb
        skos:editorialNote "Lukket bemerkning: <lukket-bemerkning>"@nb
        skos:scopeNote "Se også: <gen-se-ogsa-henvisning>"@nb
        skos:broader <http://data.ub.uio.no/usvd/<overordnetterm-id>
        skos:broader <http://data.ub.uio.no/usvd/<ox-id>
        skos:related <http://data.ub.uio.no/usvd/<se-ogsa-id>

#### Foreløpig håndtering av klassifikasjonskoder (Dewey-notasjon)

* Klassifikasjonskode (Dewey-notasjon) legges i `skos:notation`, med
  datatype `<http://dewey.info/schema-terms/Notation>`, ikke som mappinger.

* Alle tegn utenom tall, punktum og bindestrek fjernes.
  Eksempelvis blir «005.133Basi» konvertert til «005.133»
  ([USVD00332](http://wgate.bibsys.no/gate1/SHOW?objd=USVD00332&base=USVDEMNE)),
  «b 394.109411» til «394.109411»
  ([USVD45296](http://wgate.bibsys.no/gate1/SHOW?objd=USVD45296&base=USVDEMNE)),
  og «372.1103/kl» til «372.1103»
  ([USVD45366](http://wgate.bibsys.no/gate1/SHOW?objd=USVD45366&base=USVDEMNE)).
  Hvis færre enn tre gyldige tegn gjenstår utelates feltet.
  Dette er sannsynligvis feilinnførsler. Se f.eks.
  [USVD34368](http://wgate.bibsys.no/gate1/SHOW?objd=USVD34368&base=USVDEMNE)
  der «Tai språk (språkgruppe)» er fylt inn i feltet for klassifikasjonskode.

* I noen poster blir feltet gjentatt, f.eks.
  [USVD00007](http://wgate.bibsys.no/gate1/SHOW?objd=USVD00007&base=USVDEMNE).
  Vi bruker kun den første (gyldige) verdien, og ignorerer påfølgende verdier.
  Dette gjelder 58 poster, som er listet opp
  [her](https://gist.github.com/danmichaelo/7abb4bc60bce75e7b93c) så vi kan
  sjekke konsekvensene av dette (Listen er generert av
  `list_multiple_signatures.xq`).

* Feltet kan inneholde rekker, som «011-016»
  ([USVD00393](http://wgate.bibsys.no/gate1/SHOW?objd=USVD00393&base=USVDEMNE)).
  Disse beholdes som de er, selv om de ikke kan brukes i mappingprosjektet.
  Hvis de fører til støy kan vi evt. fjerne dem.

#### Andre merknader

* Se-henvisninger mappes til skos:altLabel. De beholder ikke egne identifikatorer.
  Vi *kan* beholde disse ved å bruke SKOS-XL, men foreløpig seg jeg ikke noe poeng
  med det. Må diskuteres!

* Elementet `<underemnefrase>` ignoreres. Jeg er usikker på feltets betydning,
  og det er bare [brukt 22 ganger](https://gist.github.com/danmichaelo/fb3afc5ab9a161dfae7d)
  (Listen er generert av `list_underemnefrase.xq`).

### Bruk:

XQuery-scriptet kan kjøres med f.eks. [Zorba](http://www.zorba.io/):

    $ zorba -i convert.xq >| USVDregister.rdf.xml

Konvertering fra RDF/XML til RDF/Turtle kan gjøres med f.eks.
[Rapper](http://librdf.org/raptor/rapper.html):

    $ rapper -i rdfxml -o turtle USVDregister.rdf.xml >| USVDregister.ttl

### Lisens

Dataene ble lagt ut i forbindelse med prosjektet
[tesaurus-mapping](http://www.ub.uio.no/om/prosjekter/tesaurus/)
høsten 2014.
De er tilgjengelige under [CC0 1.0](//creativecommons.org/publicdomain/zero/1.0/deed.no).
