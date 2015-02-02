#!/bin/sh

VOC=$1
if [ -z "$VOC" ]; then
    echo "Vocabulary name needed as first argument"
    exit 1
fi

if [ ! -d "$VOC" ]; then
    echo "Invalid vocabulary: $VOC"
    exit 1
fi

echo "Vocabulary: $VOC"
echo "Inferring and adding skos:narrower"
python /opt/skosify-1.0/skosify.py --no-enrich-mappings --narrower --no-mark-top-concepts --infer /opt/datakilder/$VOC/$VOC.ttl -o /opt/datakilder/$VOC/$VOC-skosify.ttl
echo "Pushing data to Fuseki"
/opt/fuseki/s-put http://localhost:3030/ds/data http://data.ub.uio.no/$VOC /opt/datakilder/$VOC/$VOC-skosify.ttl
rm /opt/datakilder/$VOC/$VOC-skosify.ttl
echo "Done!"

