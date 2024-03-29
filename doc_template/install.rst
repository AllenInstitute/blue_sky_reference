Install Guide
=============

This guide is a resource for using the Blue Sky Workflow Engine package.
It is maintained by the `Allen Institute for Brain Science <http://www.alleninstitute.org/>`_.

The package was developed and tested with Python 3.6 installed.
Behavior may be inconsistent with other Python versions.

Using Conda and Pip from Git
----------------------------

First ensure you have `pip <http://pypi.python.org/pypi/pip>`_ installed.
It is included with the Anaconda distribution.

::

    WORKING_DIR=/path/to/working/directory
    cd $WORKING_DIR

    git clone https://github.com/AllenInstitute/blue_sky_workflow_engine.git
    git clone https://github.com/AllenInstitute/blue_sky_reference.git
    conda create --name blue_sky python=3.6
    export PYTHONPATH=$WORKING_DIR/blue_sky_reference:$WORKING_DIR/blue_sky_workflow_engine

    cd blue_sky_workflow_engine
    conda activate blue_sky
    pip install -r requirements.txt
    pip install -r test_requirments.txt
    cd ../blue_sky_reference

    make test

Required Dependencies
---------------------

 * Django
 * Celery
 * Pika

Optional Dependencies
---------------------

 * `pytest <http://pytest.org/latest>`_
 * `coverage <http://nedbatchelder.com/code/coverage>`_

Installation with Docker (Optional)
-----------------------------------

`Docker <http://www.docker.com/>`_ is an open-source technology
for building and deploying applications with a consistent environment
including required dependencies.
Blue Sky workflow engine is not distributed as a Docker image,
but example Dockerfiles are available.

 #. Ensure you have Docker installed.

 #. Use Docker to build the image::
 
     cd $WORKING_DIR
     cd blue_sky_reference/docker
     docker build --tag alleninstitute/blue_sky:demo .
 
 #. Run tests in the docker image::
 
     cd $WORKING_DIR
     docker run -i -t -v `pwd`:/source alleninstitute/blue_sky:demo /bin/bash

     export PYTHONPATH=/source/blue_sky_workflow_engine:/source/blue_sky_reference
     export BLUE_SKY_SETTINGS=/source/blue_sky_reference/config/blue_sky_settings.yml
     conda activate /conda_envs/py_36

     cd /source/blue_sky_reference
     make test

     exit

 #. Edit blue_sky_reference/blue_sky/settings.py

    - change BLUE_SKY_HOSTNAME='localhost' to the hostname of the machine you will be running on

 #. Run the reference app in docker compose::

     cd $WORKING_DIR
     cd blue_sky_reference/config
     docker-compose up -d
     docker-compose exec -u blue_sky_user blue_sky /bin/bash

     source activate /conda_envs/py_36
     export PYTHONPATH=/source/blue_sky_reference:/source/blue_sky_workflow_engine
     export DEBUG_LOG=dbg.log

     cd /home/blue_sky_user/work
     python -m workflow_engine.management.manage showmigrations
     python -m workflow_engine.management.manage migrate
     python -m workflow_engine.management.manage createsuperuser
     python -m workflow_engine.management.manage collectstatic

     mkdir -p /home/blue_sky_user/work/notebooks
     cp /source/blue_sky_reference/config/workflow_config.yml /home/blue_sky_user/work

     python -m workflow_engine.management.manage import_workflows /home/blue_sky_user/work/workflow_config.yml
     python -m workflow_engine.management.manage help

     /source/blue_sky_reference/restart_workers.sh blue_sky /home/blue_sky_user/work /home/blue_sky_user/work/logs /source/blue_sky_reference:/source/blue_sky_workflow_engine

 #. Use a web browser to navigate to http://<hostname>:9001
    - Celery level messaging is available in the Flower monitor
    - Rabbit level messaging is available in the Rabbit monitor
    - A Jupyter notebook server is available in the Jupyter link

    - The Admin console is available in admin.
        - look under workflow_engine / workflows for a graphical view of the workflow
        - note that no observations or calibrations have been processed

 #. Run an example ingest::

     # if you are not already in the docker container...
     cd $WORKING_DIR
     cd blue_sky_reference/config
     docker-compose exec -u blue_sky_user blue_sky /bin/bash

     source activate /conda_envs/py_36
     export PYTHONPATH=/source/blue_sky_reference:/source/blue_sky_workflow_engine
     export DEBUG_LOG=dbg.log

     # in the docker container
     cd /source/blue_sky_reference/example
     python example_ingest.py

 #. Manually approve the waiting Observation objects

    - In the admin console / workflow_engine /workflow view note that proccessing is stopped at the mock_wait state.
    - Go into the admin console / blue_sky / observations
    - Select the rows in the QC_FAILED state
    - Change the Action dropdown to 'Manual qc pass' and click 'Go'.
    - In the admin console / workflow_engine /workflow view note that proccessing has continued through to the end of the workflow.

 #. To kill the server::

     # in the docker container
     pkill -9 -f python

 #. To restart the server run the full restart_workers.sh command again.

 #. To take down the docker containers::

     # in the docker host
     cd $WORKING_DIR/blue_sky_reference/config

     docker-compose down

