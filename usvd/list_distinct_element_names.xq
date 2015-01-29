(: Return all distinct element names :)

<nodes>
{
	for $x in distinct-values(doc('usvd.xml')//*/name())
	return element {$x} {''}
}
</nodes>
