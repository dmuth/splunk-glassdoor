#!/bin/bash
#
# Build our Python app
#

# Errors are fatal
set -e

#
# Change to the parent of this script
#
pushd $(dirname $0) > /dev/null
cd ..

echo "# "
echo "# Building Docker containers..."
echo "# "
docker build . -f Dockerfile-python -t splunk-glassdoor-python
docker build . -f Dockerfile-splunk -t splunk-glassdoor

echo "# "
echo "# Tagging container..."
echo "# "
docker tag splunk-yelp-python dmuth1/splunk-glassdoor-python
docker tag splunk-yelp dmuth1/splunk-glassdoor

echo "# Done!"

