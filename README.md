## Datakilder for tesaurus-mapping

Her ligger åpne datakilder for prosjektet
[tesaurus-mapping](http://www.ub.uio.no/om/prosjekter/tesaurus/),
samt kode for konvertering til RDF.
Både data og kode er lisensiert med
[CC0 1.0](//creativecommons.org/publicdomain/zero/1.0/deed.no),
med unntak av Tekord, som er lisensiert under ODC-PDDL.

Mer informasjon finnes i README-filene for hver datakilde:

 - [UBOs emneregister til Dewey](usvd/README.md)
 - [HUMORD](humord/README.md)
 - [Katalogdata](katalog/README.md)
 - [TEKORD](tekord/README.md)

Alle kildene bortsett fra katalogdata kommer fra [Emne-modulen i Bibsys](http://www.ub.uio.no/fag/ehylle/14k019572.pdf)
og konverteres til RDF med XQuery-scriptet `emneregister.xq`. Etterpå gjøres en postprossesering med Skosify, som kan
installeres med

    pip install git+git://github.com/danmichaelo/skosify.git

(Hvis du ikke har `pip`, installer `python-setuptools`)

Crontab:

Bibsys legger ut oppdatert Humord-XML hver mandag klokka 07 UTC.
0715 henter vi filen, konverterer til RDF, gjør en commit og dytter til utv.uio.no.

    15 7 * * 1 cd /projects/datakilder && ./tools/publish.sh humord 2>&1 | tee out.log

0730 oppdaterer vi Fuseki på en annen maskin:

    30 7 * * 1 cd /opt/datakilder && git pull uio master && ./tools/update-fuseki.sh humord

Repoet speiles til GitHub hver time:

    30 * * * * cd /projects/github-mirrors/datakilder.git/ > /dev/null; git fetch --quiet && git push --quiet --mirror github
