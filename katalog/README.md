## Klassifikasjons- og indekseringsdata fra bibliografiske katalogposter

### Innhold

Datasettet `bib.ttl` baserer seg på et uttrekk fra BIBSYS' katalog-modul
den 28. april 2014, med emneord og klassifikasjon for alle bibliografiske poster i
BIBSYS-katalogen. Kildefilene er i BIBSYSMARC i en serialisering som trolig ikke
har noe navn, men med det ligger veldig nært det
[YAZ](http://www.indexdata.com/yaz/doc/yaz-marcdump.html)
kaller ‘line-format’. En enkel eksempelpost kan se slik ut:

    *000 132089262
    *082k $2DDC-23
    $a895.68
    $b895.609002
    *698k $aKamakura
    $bPeriode
    *698k $aJapansk litteratur
    ^

mens en mer omfattende post kan se slik ut:

    *000 13208953x
    *082ud$2DDC-23
    $a302.23068
    *082up$a302.23068
    *082uv$2DDC-23
    $a302.23068
    $b338.456130223
    $b338.4730223
    $x(1)0685
    *082k $2DDC-23
    $a302.23068
    *082un$2DDC-23
    $a302.23068
    *082uk$2DDC-23
    $a302.23068
    *082ug$2DDC-23
    $a302.23
    *082uh$a302.23068
    *082ur$2DDC-23
    $a302.23068
    *082d $2DDC-23
    $a302.23068
    *082c $2DDK-5
    $a302.23
    $b302.23068
    *687ud$aMassemedia : Administrasjon
    *687ud$aMassemedia : Ledelse
    *691**$amedieverksemder verksemdsendringar mediavirksomheter endringer media
    *698c $aKonvergens
    $bTeknologi
    *698c $aMedier
    *698c $aInnovasjon
    *698c $aEndring
    *698c $aMediekonvergens
    *698c $aSosial endring
    ^

For enklere prosessering kan vi trekke ut dataene vi er interessert i (f.eks. 698 og 082)
og omgjøre til tabellformat (årstall er igjen tatt fra de to første sifrene i objektid):

| År      | Objektid    | Skjema    | Term/notasjon          | Bibliotek |
|---------|-------------|-----------|------------------------|-----------|
| 2013    | 13208953x   | ddc       | 302.23068              | up        |
| 2013    | 13208953x   | ddc       | 302.23068              | uv        |
| 2013    | 13208953x   | ddc       | 338.456130223          | uv        |
| 2013    | 13208953x   | ddc       | 338.4730223            | uv        |
| 2013    | 13208953x   | ddc       | 302.23068              | k         |
| 2013    | 13208953x   | ddc       | 302.23068              | un        |
| 2013    | 13208953x   | ddc       | 302.23068              | uk        |
| 2013    | 13208953x   | ddc       | 302.23                 | ug        |
| 2013    | 13208953x   | ddc       | 302.23068              | uh        |
| 2013    | 13208953x   | ddc       | 302.23068              | ur        |
| 2013    | 13208953x   | ddc       | 302.23068              | d         |
| 2013    | 13208953x   | ddc       | 302.23                 | c         |
| 2013    | 13208953x   | ddc       | 302.23068              | c         |
| 2013    | 13208953x   | humord    | Konvergens (Teknologi) | c         |
| 2013    | 13208953x   | humord    | Medier                 | c         |
| 2013    | 13208953x   | humord    | Innovasjon             | c         |
| 2013    | 13208953x   | humord    | Endring                | c         |
| 2013    | 13208953x   | humord    | Mediekonvergens        | c         |
| 2013    | 13208953x   | humord    | Sosial endring         | c         |

* Her har jeg valgt å ikke ta med utgave fordi det er [så få innførsler](http://biblionaut.net/bibsys-emnedata/#ddc)
der dette er angitt at det fungerer dårlig som filtreringskriterium.
* Merk at praksis for emneord er at det samme emneordet ikke gjentas av ulike bibliotek, mens det for klassifikasjon er at hvert bibliotek klassifiserer, uavhengig av om klassenummeret finnes på posten fra før.

### Konvertering

Ved hjelp av Python-scriptet `convert.py` og [rdflib](https://github.com/RDFLib/rdflib)
trekker vi ut data fra Universitetsbiblioteket i Oslo (UBO, bibkode 'k'), og uttrykker
dette i RDF. Posten ovenfor blir seende slik ut med Turtle-serialisering:

    <http://data.ub.uio.no/bib/res/132089262> a dct:BibliographicResource
        dct:subject <http://data.ub.uio.no/humord/06922> ,
            <http://data.ub.uio.no/humord/11073> ,
            <http://dewey.info/class/895.68/e23/> ;



        ubo:classification <http://data.ub.uio.no/bib/classification/ddc/23/895.68>

    <http://data.ub.uio.no/bib/classification/ddc/23/895.68> a skos:Concept
        skos:broader <http://data.ub.uio.no/bib/classification/ddc/895.68>

    ALT B)
        ubo:ddc "895.68"
        ubo:ddc23 "895.68"

Foreløpig henter vi bare ut HUMORD-indeksering (`698k`)
og DDC23-klassifikasjon (`082k $2DDC-23`).

### Fra Humord-term til identifikator

* Humords identifikatorer ligger ikke i katalogdataene. Disse må derfor søkes
  opp fra termene. Scriptet søker opp URIer fra data i `../humord/humord.ttl`.

* Spesialtegn er kodet annerledes i katalogdataene enn i emneregisteret, så vi
  må mappe mellom de. Eksempelvis er `ä` kodet som `@æ`. Mappinger for de
  vanligste tegnene er lagt inn.

* En del termer i de bibliografiske postene lar seg ikke
  gjenfinne i Humord, delvis på grunn av endringer i Humord siden 28. april 2014,
  og delvis på grunn av rene feil i postene. F.eks. finnes termen "Edo" på
  [932311695](http://ask.bibsys.no/ask/action/show?kid=biblio&visningsformat=bibsysmarc&pid=932311695),
  men denne finnes ikke uten kvalifikator [i Humord](http://wgate.bibsys.no/gate1/FIND?bd=Edo&base=HUMORD&type=search).

  [Fullstendig liste](https://gist.github.com/danmichaelo/a3535d9239eecd9fa4b4)
  over termer som ikke ble gjenfunnet i Humord.  

### Andre merknader
* Identifikator for bibliografiske poster i BIBSYS (objektid) består av 9 tegn,
  og kan inneholde tall samt 'x', eks.: `13405346x`. Vi bygger URIer fra objektid-ene
  ved å bruke navnerommet `http://data.ub.uio.no/kat/`.
  Eks.: `<http://data.ub.uio.no/bib/13405346x>`.

* Alle tegn utenom tall, punktum og bindestrek fjernes fra Dewey-notasjonen.
  Eksempelvis blir «f 781.2» konvertert til «781.2»
  ([910664404](http://ask.bibsys.no/ask/action/show?kid=biblio&visningsformat=bibsysmarc&pid=910664404)),
  «971.1 How» til «971.1»
  ([981446469](http://ask.bibsys.no/ask/action/show?kid=biblio&visningsformat=bibsysmarc&pid=981446469)).

### Kildefiler

Lisens for kildefilene er ikke avklart, så de er foreløpig ikke lagt inn her.
Bibsys bruker Norsk lisens for offentlige data på [Bibliografiske data på data.norge.no](http://data.norge.no/data/bibsys/bibsys-bibliotekbase-bibliografiske-data-sru), så de faller trolig inn under den.

For å hente og pakke ut kildefilene (113 MB komprimert):

    wget -O katklassdump.tbz2 https://dl.dropboxusercontent.com/u/1007809/data/katklassdump.tbz2
    tar -xvf katklassdump.tbz2

For å lage `bib.ttl` fra kildefilene, kjør `python convert.py`
