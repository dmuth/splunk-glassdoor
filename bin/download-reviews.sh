#!/bin/bash
#
# Download a URL full of reviews
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

$THIS_DIR/download-reviews.py $URL

