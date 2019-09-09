#!/bin/bash
docker build --tag alleninstitute/blue_sky_base . 2>&1 | tee docker_build.log 
#docker tag alleninstitute/blue_sky docker.aibs-artifactory.corp.alleninstitute.org/blue_sky_base
#docker push docker.aibs-artifactory.corp.alleninstitute.org/blue_sky

