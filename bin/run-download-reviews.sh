#!/bin/bash
#
# Build our Docker container
#

# Errors are fatal
set -e

pushd $(dirname $0)/.. > /dev/null

echo "# "
echo "# Building container..."
echo "# "
docker build . -f Dockerfile-python -t splunk-glassdoor-python
docker tag splunk-glassdoor-python dmuth1/splunk-glassdoor-python

CMD=""

DOCKER_V_LOGS="-v $(pwd)/logs:/logs"
docker run -it ${CMD} ${DOCKER_V_LOGS} splunk-glassdoor-python $@

