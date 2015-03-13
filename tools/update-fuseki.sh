#!/bin/bash
#
# This script puts data to Fuseki
#
# Set RUBYENV to the value returned from `rvm env --path` to make the script find
# the RVM environment when run as a cronjob.
#
# Example:
#  30 7 * * 1 RUBYENV=/usr/local/rvm/environments/ruby-1.9.3-p551@global cd /opt/datakilder && git pull uio master && ./tools/update-fuseki.sh humord | tee -a update-fuseki.log


VOC=$1
if [ -z "$VOC" ]; then
    echo "Vocabulary name needed as first argument"
    exit 1
fi

if [ ! -d "$VOC" ]; then
    echo "Invalid vocabulary: $VOC"
    exit 1
fi

echo "$(date +'%Y-%M-%d %H:%m:%S %Z') - Job 'update-fuseki' starting"

if [ -n "$RUBYENV" ]; then
  source "$RUBYENV"
fi

echo "Vocabulary: $VOC"
echo "Inferring and adding skos:narrower"
python /opt/skosify/skosify/skosify.py --no-enrich-mappings --transitive --narrower --no-mark-top-concepts --infer /opt/datakilder/$VOC/$VOC.ttl -o /opt/datakilder/$VOC/$VOC-skosify.ttl
echo "Pushing data to Fuseki"
/opt/fuseki/s-put http://localhost:3030/ds/data http://data.ub.uio.no/$VOC /opt/datakilder/$VOC/$VOC-skosify.ttl
rm /opt/datakilder/$VOC/$VOC-skosify.ttl
echo "$(date +'%Y-%M-%d %H:%m:%S %Z') - Job 'update-fuseki' complete"

