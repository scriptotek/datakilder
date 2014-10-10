(: Return all distinct element names :)

<nodes>
{
	for $x in distinct-values(doc('USVDregister.xml')//*/name())
	return element {$x} {''}
}
</nodes>
