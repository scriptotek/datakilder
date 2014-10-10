
(: Strip off non-valid characters, return only non-empty elements :)
declare function local:signatures($sigs as element()*)
as element()*
{
    for $sig in $sigs
    let $s := replace( $sig/text(), '[^0-9.-]', '' )
    where $s != ''
    return <signature>{ $s }</signature>
};

(: Return all posts with more than one valid <signature> :)
{
    for $post in doc( 'USVDregister.xml' )/usvd/post
    let $sigs := local:signatures( $post/signatur )
    where count($sigs) > 1
    return <post>
              { $post/term-id }
              { $post/hovedemnefrase }
              { $sigs }
           </post>
}
