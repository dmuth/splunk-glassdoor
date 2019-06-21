#!/bin/bash
#
# Download a review
#

# Errors are fatal
set -e

if test "$1" == "" -o "$1" == "-h" -o "$1" == "--help"
then
	echo "! "
	echo "! Symtax: $0 url"
	echo "! "
	echo "! url - URL of a venue on Glassdoor"
	echo "! "
	exit 1
fi

URL=$1

THIS_DIR=$(dirname $0)

TARGET=logs/$(echo $URL | sed -e "s/.*\///").json

if test -f $TARGET
then
	echo "# Target '${TARGET}' exists, skipping..."

else
	TMP=$(mktemp)
	$THIS_DIR/download-reviews.py $URL > $TMP
	mv $TMP $TARGET

fi



