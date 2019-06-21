#!/bin/bash
#
# Download reviews from all of our restaurants
#

# Errors are fatal
set -e

if test "$1" == "" -o "$1" == "-h" -o "$1" == "--help"
then
	echo "! "
	echo "! Symtax: $0 file"
	echo "! "
	echo "! file - Text file of Yelp venue URLs to grab comments from."
	echo "! "
	exit 1
fi

URLS=$1
THIS_DIR=$(dirname $0)


for URL in $(cat $URLS)
do
	$THIS_DIR/download-reviews.sh $URL 

done



