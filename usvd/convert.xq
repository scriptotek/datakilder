import module namespace emneregister="http://ub.uio.no/emneregister"
  at "../emneregister.xq";

declare namespace marcxml = "http://www.loc.gov/MARC21/slim";
declare namespace rdf     = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
declare namespace rdfs    = "http://www.w3.org/2000/01/rdf-schema#";
declare namespace skos    = "http://www.w3.org/2004/02/skos/core#";
declare namespace dcterms = "http://purl.org/dc/terms/";

declare variable $scheme := 'http://data.ub.uio.no/usvd/';
declare variable $uri_base := 'http://data.ub.uio.no/usvd/';


(: To test a specific post: :)
(: emneregister:post(doc('USVDregister.xml')/usvd/post[descendant::term-id/text()="USVD21236"]) :)

emneregister:toRdf( doc( 'USVDregister.xml' )/usvd/post, $scheme, $uri_base, 'ddc' )
