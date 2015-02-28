import module namespace emneregister="http://ub.uio.no/emneregister"
  at "../emneregister.xq";

declare namespace rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
declare namespace owl = "http://www.w3.org/2002/07/owl#";
declare namespace skos = "http://www.w3.org/2004/02/skos/core#";
declare namespace dct = "http://purl.org/dc/terms/";

declare variable $scheme := 'http://data.ub.uio.no/tekord';
declare variable $uri_base := 'http://data.ub.uio.no/tekord/c';

declare function local:addSameAs($doc as node()?) {
    element { $doc/name() } {
    	$doc/@*,
    	for $record in $doc/node()
	    return element { $record/name() } {
	    	$record/@*,
	    	if ($record/dct:identifier) then
		        <owl:sameAs rdf:resource="http://ntnu.no/ub/data/tekord#{ $record/dct:identifier/text() }"/>
		    else (),
	        for $node in $record/node()
	        return $node
	    }
	}
};

local:addSameAs(emneregister:toRdf( doc( 'tekord.xml' )/ntub/post, $scheme, $uri_base, 'udc'))
