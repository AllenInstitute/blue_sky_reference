Developers Guide
================

This guide is a resource for using the Blue Sky Workflow Engine package.
It is maintained by the `Allen Institute for Brain Science <http://www.alleninstitute.org/>`_.

The Blue Sky Workflow Engine uses a Celery Task Queue with a RabbitMQ broker to
manage job submissions to a Portable Batch System (PBS) job scheduler.
It organizes job queues using a workflow graph and a Django PostgreSQL database model to
store information about the equeued objects. The Django Admin plugin provides user interface features.

Support features include
a `PyTest <https://docs.pytest.org/en/latest/>`_ test suite, 
code coverage with `pytest-cover <https://pytest-cov.readthedocs.io/en/latest/>`_,
linting using `prospector <https://prospector.readthedocs.io/en/master/>`_,
`Sphinx <http://www.sphinx-doc.org/en/master/>`_ documentation,
`Pip packaging <https://python-packaging.readthedocs.io/en/latest/>`_,
and a Docker build.

Celery Task Queue and RabbitMQ Broker
-------------------------------------

The workflow engine is largely based on the integration of a Celery (over RabbitMQ)
messaging system with a Django data model and admin plugin.
As much as possible, the workflow engine is modeled after examples in the documentation.

 * `Celery <http://www.celeryproject.org/>`_
 * `RabbitMQ <https://www.rabbitmq.com/>`_

 * `Using Celery with Django <http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`_
 * `Celery Routing <http://docs.celeryproject.org/en/latest/userguide/routing.html>`_
 * `Celery Workflows with Canvas chains <http://docs.celeryproject.org/en/latest/userguide/canvas.html#chains>`_
(note: the workflow engine no longer makes significant use of chains)

Monitoring Tools:
 * `Flower Monitor <http://flower.readthedocs.io/en/latest/>`_
 * `RabbitMQ Management <https://www.rabbitmq.com/management.html>`_

Django Web Framework and Admin Plugin
-------------------------------------

 * `Django <https://www.djangoproject.com/>`_
 * `Admin Plugin <https://docs.djangoproject.com/en/2.0/ref/contrib/admin/actions/>`_

Settings
--------

The primary location of settings are in two files specified by environment variables:

$DJANGO_SETTINGS_MODULE - examples of these are found in blue_sky/settings.py
$BLUE_SKY_SETTINGS - examples of these are found in config/blue_sky_settings.yml

The `Django settings module <https://docs.djangoproject.com/en/2.2/topics/settings/>`_
is well documented, but most current deployments have a fairly similar form to the examples provided.

blue_sky_settings.yml uses Celery `lowercase settings <https://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings>`_
The examples provided give the endpoint of the message broker as well as timeout settings
for broker connection (including in processes that only send but do not handle messages).

Environments
------------

The workflow in production mode requires several Python environments.
Generally `Anaconda <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_
is used to set these environments up, but venv or creative $PYTHONPATH management
might also work. The `circus <https://circus.readthedocs.io/en/latest/>`_ process
manager required a Python 2.7 environment at the time it was implemented.
All other processes may share a Python 3.7 environment with dependencies installed
from the workflow engine's requirements.txt file. Executables can run in their own
anaconda environment, which is set in the PBS template.  The response messages
are sent back from the compute cluster using an environment installed on that system.

Note: It is possible to share the primary and response environments, but they must be installed
and accessed while mounted on the same directory path or the anaconda "source activate" script
will get confused.

Users and Permissions
---------------------

Note that when writing input.json and data files to a SAN, the directory must
have setgid set properly or an equivalent setting.

Note that when running in a docker environment, the blue_sky_user must be
set to use the production user id.

The Jupyter notebook, the Django admin console, the Moab endpoint, and the
message broker and the database all have credentials that need to be set and managed.
This requires further documentation.

Logging
-------

Logging is primarily configured using the 
Python `logging package <https://docs.python.org/3.7/howto/logging.html>`_.
For each Django-aware process, the logging dict is present in setup.LOGGING
in the `Django settings module <https://docs.djangoproject.com/en/2.2/topics/settings/>`_.
It is suggested that the log levels be adjusted for different contexts (dev, production, etc).

In order to have each worker process log to a different file, the $DEBUG_LOG
environment variable is substituted into the setup.LOGGING dict.
The :class:`workflow_engine.process.process_manager` module sets this variable
as it starts the processes.

Celery tasks have some specific logging configuration quirks.
In order to use the standard logging system, the logger needs to be configured
in the after_setup_logger signal handler
as described in the `celery logging documentation <https://docs.celeryproject.org/en/latest/userguide/tasks.html#logging>`_.
The handler is imported from :func:`workflow_engine.celery.setup_logging_handler.configure_logging_from_settings`.
The Django processes (all of them) 
that use :func:`workflow_engine.client_settings.configure_worker_app`
will do this automatically using celery's `app.conf.imports <https://docs.celeryproject.org/en/latest/userguide/configuration.html#example-configuration-file>`_
configuration setting.

Builds
------

There is no current continuous build configured.
Most operations can be run through the Makefile.
Some operations are handled by scripts and a Makefile in the blue_sky/docker subdirectory.
This includes anaconda environment deployment, which is currently incomplete.

Development Deployment
----------------------

There is a docker-compose file in blue_sky/config.  It can be started with::

    docker-compose up -d
    docker-compose exec -u blue_sky_user blue_sky /bin/bash

    source activate /conda_envs/py_37
    export DEBUG_LOG=dbg.log

    python -m workflow_engine.management.manage showmigrations
    python -m workflow_engine.management.manage migrate
    python -m workflow_engine.management.manage createsuperuser
    python -m workflow_engine.management.manage collectstatic
    python -m workflow_engine.management.manage import_workflows /home/blue_sky_user/work/workflow_config.yml
    python -m workflow_engine.management.manage help

    restart_workers.sh blue_sky /home/blue_sky_user/work

At this point you can navigate to http://localhost:9001/ with a web browser.
