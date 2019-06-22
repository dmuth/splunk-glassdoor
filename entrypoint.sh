#!/bin/bash
#
# Entrypoint script--determine what it is we want to do.
#


if test "$1"
then

	if test "$1" == "--devel"
	then
		echo "# "
		echo "# Starting container in devel mode and spawning a bash shell..."
		echo "# "
		exec "/bin/bash"

	elif test "$1" == "--url"
	then
		URL=$2
		echo "# "
		echo "# Downloading URL ${URL}..."
		echo "# "
		/app/download-reviews.sh $URL

	else 
		#
		# Assume we're downloading a file full of URLs...
		#
		FILE=$1
		echo "# "
		echo "# Downloading URLs in file ${FILE}..."
		echo "# "
		/app/download-reviews-from-file.sh /mnt/$FILE

	fi

else
	echo "! "
	echo "! Syntax: $0 ( --devel | --url URL | file.txt )"
	echo "! "
	echo "! file.txt - File containing one URL per line to download."
	echo "! "
	exit 1

fi


