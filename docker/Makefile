BUILDDIR = build
ENV_BUILDDIR = build_env
ARTIFACTORY_REPO=docker.aibs-artifactory.corp.alleninstitute.org
ARTIFACTORY_TAG=staging
VERSION=0.121.0
CONDA_ENVS = /local1/conda_envs/$(VERSION)
BSWE_DIR = /local1/git/blue_sky_workflow_engine
APP_NAME=blue_sky
APP_DIR=/local1/git/$(APP_NAME)
APP_DEPLOY_DIR=/local1/app_dirs
MOUNTS  = -v $(CONDA_ENVS):/conda_envs -v $(BSWE_DIR):/source/blue_sky_workflow_engine -v $(APP_DIR):/source/$(APP_NAME) -v $(APP_DEPLOY_DIR):/app_dir
PYTHONPATH = --env PYTHONPATH=/app_dir
PYTEST = /bin/bash -c "source activate /conda_envs/py_37; pytest"
USER_FLAG = -u blue_sky_user

build:
	mkdir -p $(BUILDDIR) 
	cp jupyter_notebook* create_conda_envs.sh install_app_dirs.sh Dockerfile $(BUILDDIR)
	cd $(BUILDDIR); docker build --tag alleninstitute/blue_sky_base . 2>&1 | tee docker_build.log 

conda_envs:
	docker run -e APP_NAME=$(APP_NAME) $(USER_FLAG) $(MOUNTS) -it alleninstitute/blue_sky_base /create_conda_envs.sh

install_app_dirs:
	docker run -e APP_NAME=$(APP_NAME) $(USER_FLAG) $(MOUNTS) -it alleninstitute/blue_sky_base /install_app_dirs.sh

test:
	docker run -u root $(USER_FLAG) $(MOUNTS) $(PYTHONPATH) --workdir /source/$(APP_NAME) -it alleninstitute/blue_sky_base $(PYTEST)

tag_for_artifactory:
	docker tag alleninstitute/blue_sky_base ${ARTIFACTORY_REPO}/blue_sky_base:$(ARTIFACTORY_TAG)

push_to_artifactory:
	docker push ${ARTIFACTORY_REPO}/blue_sky_base:$(ARTIFACTORY_TAG)


FORCE:

clean:
	rm -rf $(BUILDDIR)
