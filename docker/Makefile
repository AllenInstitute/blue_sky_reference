PROJECTNAME = blue_sky_base
BUILDDIR = build
ENV_BUILDDIR = build_env
VERSION=0.121.0
CONDA_ENVS = /local1/conda_envs/$(VERSION)
BSWE_DIR = /local1/git/blue_sky_workflow_engine
BLUE_SKY_DIR = /local1/git/blue_sky
MOUNTS  = -v $(CONDA_ENVS):/conda_envs -v $(BSWE_DIR):/blue_sky_workflow_engine -v $(BLUE_SKY_DIR):/blue_sky
PYTHONPATH = --env PYTHONPATH=/blue_sky:/blue_sky_workflow_engine
PYTEST = /bin/bash -c "source activate /conda_envs/py_37; pytest"
USER = -u blue_sky_user

build:
	mkdir -p $(BUILDDIR) 
	cp jupyter_notebook* create_conda_envs.sh Dockerfile $(BUILDDIR)
	cd $(BUILDDIR); docker build --tag alleninstitute/blue_sky_base . 2>&1 | tee docker_build.log 

conda_envs:
	docker run -it $(USER) $(MOUNTS) alleninstitute/blue_sky_base ./create_conda_envs.sh

test:
	docker run -u root -it $(USER) $(MOUNTS) $(PYTHONPATH) --workdir /blue_sky alleninstitute/blue_sky_base /bin/bash #$(PYTEST)

FORCE:

clean:
	rm -rf $(BUILDDIR)
