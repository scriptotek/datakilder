(: Return all posts with letters or other characters outside [0-9.-] in the <signature> field :)

{
    for $post in doc('USVDregister.xml')/usvd/post
    where
    {
        for $sig in $post/signatur
        return xs:integer(not(matches(data($sig), '^[0-9.-]+$')))
    } > 0
    return <post>
              { $post/term-id }
              { $post/hovedemnefrase }
              { $post/signatur }
           </post>
}
