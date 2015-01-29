#!/bin/sh

# Go to parent directory of the script directory
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs dirname )
cd "$DIR"

#==========================================================
# Get options
#==========================================================

DUMPS_DIR=$(awk -F "=" '/dumps_dir/ {print $2}' config.ini)

if [ -z "$DUMPS_DIR" ]; then
    echo "No dumps_dir given in config.ini"
    exit 1
fi
if [ ! -d "$DUMPS_DIR" ]; then
    echo "dumps_dir doesn't exist"
    exit 1
fi

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

#==========================================================
# Configure virtualenv
#==========================================================

function install_deps
{
    echo Installing/updating dependencies
    pip install -U git+git://github.com/danmichaelo/skosify.git git+https://github.com/juanique/python-virtuoso
    xc=$?

    if [ $xc != 0 ]; then
        echo
        echo -----------------------------------------------------------
        echo ERROR:
        echo Could not install dependencies using pip
        echo -----------------------------------------------------------
        exit 1
    fi
}

if [ ! -f ENV/bin/activate ]; then

    echo
    echo -----------------------------------------------------------
    echo Virtualenv not found. Trying to set up
    echo -----------------------------------------------------------
    echo
    virtualenv ENV
    xc=$?

    if [ $xc != 0 ]; then
        echo
        echo -----------------------------------------------------------
        echo ERROR:
        echo Virtualenv exited with code $xc.
        echo You may need to install or configure it.
        echo -----------------------------------------------------------
        exit 1
    fi

    echo Activating virtualenv
    . ENV/bin/activate

    install_deps

else

    echo Activating virtualenv
    . ENV/bin/activate

fi

#==========================================================
# Pull in code changes
#==========================================================

git checkout master
git pull origin master

xc=$?
if [ $xc != 0 ]; then

    echo
    echo -----------------------------------------------------------
    echo ERROR:
    echo Could not git pull. Conflict?
    echo -----------------------------------------------------------
    exit 1

fi

#==========================================================
# Pull in vocabulary changes and convert to RDF
#==========================================================

cd $VOC

make clean
make all

xc=$?
if [ $xc != 0 ]; then

    echo
    echo -----------------------------------------------------------
    echo ERROR:
    echo Make failed
    echo -----------------------------------------------------------
    exit 1

fi


#==========================================================
# Add changes to git, commit and push to remote
#==========================================================

git add $VOC.xml $VOC.ttl
git commit -m "Data oppdatert: $VOC"
git push origin master

#==========================================================
# Publish dumps
#==========================================================

bzip2 -k $VOC.ttl
zip $VOC.ttl.zip $VOC.ttl
cp $VOC.ttl $DUMPS_DIR/
cp $VOC.ttl.zip $DUMPS_DIR/
cp $VOC.ttl.bz2 $DUMPS_DIR/
rm *.bz2 *.zip

#==========================================================
# Update triple store 
#==========================================================

cp $VOC.ttl /tmp/$VOC.ttl
python ../tools/update-virtuoso.py "/tmp" "$VOC"

