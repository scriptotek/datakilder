(: Return all posts with <underemnefrase> :)

{
    for $post in doc("USVDregister.xml")/usvd/post[descendant::underemnefrase]
    return <post>
              {$post/term-id}
              {$post/hovedemnefrase}
              {$post/underemnefrase}
           </post>
}
