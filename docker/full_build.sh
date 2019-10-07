#!/bin/bash
DEPLOY_DIR=/local1/app_dirs/blue_sky

make clean build
make -e VERSION=0.121.0 -e APP_NAME=blue_sky -e CONDA_ENVS=/allen/aibs/pipeline/image_processing/volume_assembly/workflow_conf/conda_envs/dev conda_envs
make -e VERSION=0.121.0 APP_NAME=blue_sky -e APP_DEPLOY_DIR=$(DEPLOY_DIR) install_app_dirs

