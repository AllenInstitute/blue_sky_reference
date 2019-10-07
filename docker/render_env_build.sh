#!/bin/bash
export BLUE_SKY_VERSION=0.121.0
make clean build
make -e APP_NAME=at_em_imaging_workflow -e APP_DIR=/local1/git/at_em_imaging_workflow -e CONDA_ENVS=/allen/aibs/pipeline/image_processing/volume_assembly/conda_envs/staging conda_envs
#make -e APP_NAME=at_em_imaging_workflow -e APP_DIR=/local1/git/at_em_imaging_workflow -e APP_DEPLOY_DIR=/allen/aibs/pipeline/image_processing/volume_assembly/app_dirs/staging install_app_dirs

