#!/bin/sh

RED='\033[0;31m'
NC='\033[0m' # No Color

cleanup () {
    docker-compose -p timeline-api kill
    docker-compose -p timeline-api rm -f
}

trap 'cleanup ; echo "Interrupted"' HUP INT QUIT PIPE TERM

docker-compose -p timeline-api -f docker-compose.yml build && docker-compose -p timeline-api -f docker-compose.yml up -d
if [ $? -ne 0 ] ; then
    echo "Docker Compose Failed"
    exit -1
fi

TEST_EXIT_CODE=`docker wait timeline-api_test-runner_1`
docker-compose -p timeline-api -f docker-compose.yml logs test-runner
if [ "$TEST_EXIT_CODE" -ne 0 ] ; then
    LOG_FILE="timeline_service_test_$(date +"%Y%m%dT%H%M%S").log"
    docker logs timeline-api_timeline-api_1 > "${LOG_FILE}"
    printf "${RED}Tests Failed. See timeline_service logs in ${LOG_FILE}${NC}\n"
fi

cleanup
exit $TEST_EXIT_CODE
