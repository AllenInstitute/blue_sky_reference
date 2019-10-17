.. _messaging:

Blue Sky Messaging
==================

This guide describes messaging in the  Blue Sky Workflow Engine package.
It is maintained by the `Allen Institute for Brain Science <http://www.alleninstitute.org/>`_.

Introduction
------------

Blue Sky messaging is designed around the Celery asynchronous message queue.
The workflow engine is split into several worker processes that handle different messages,
such as starting a job, recording the finished state of a job or enqueueing an object
in the next workflow queue. Some processes only originate messages, such as the web ui server
or the jupyter notebooks.

The use of messaging clearly separate strategies from each other,
so an exception thrown at the start of a downstream strategy doesn't affect the completion of the upstream strategy.
It also allows for the enqueued objects that are processed to be cleanly split or grouped as they progress through the workflow.

Connecting to the celery broker
-------------------------------

A process that communicates through the message broker should configure a celery
app using configure_worker_app.  A worker that receives tasks should specify the
worker name in order to listen to the correct queues. Processes that only initiate messages,
but do not implement celery tasks do not need to specify 

.. code-block:: python

    import os
    import celery
    from django.conf import settings
    from workflow_client.client_settings import configure_worker_app

    app = celery.Celery('workflow')
    configure_worker_app(app, settings.APP_PACKAGE, 'workflow') 

Celery Settings
---------------

The blue_sky_settings.yml file (specified by the $BLUE_SKY_SETTINGS environment variable
contains connection parameters for the messaging system.

Incorrect configuration of these parameters can lead to poor performance or
a loss of messaging connectivity for one or all worker processes.

Different workers can all share a blue_sky_settings.yml file, but in some cases,
such as when the worker processes are running in a docker container, the
broker might be at a different url for some of the workers, requiring separate configuration files.

.. code-block:: yaml

    broker_url: pyamqp://blue_sky_user:blue_sky_user@message_queue:5672/
    result_backend: rpc://
    result_persistent: true
    task_serializer: json
    result_serializer: json
    result_expires: 3600
    broker_connection_timeout: 10
    broker_connection_retry: false
    soft_time_limit: 600
    time_limit: 2400
    accept_content: ['json']
    worker_prefetch_multiplier: 1
    timezone: US/Pacific
    enable_utc: true
    task_queue_max_priority: 10
    worker_hijack_root_logger: false
    broker_transport_options:
        max_retries: 3
        interval_start: 0
        interval_step: 10
        interval_max: 30

Celery Signatures
-----------------

The messages that are used in the workflow_engine are defined in two files.
workflow_client.signatures has most of the signatures. Messages used to communicate
with the circus process manager are in workflow_client.tasks.circus_signatures.

Signatures are used to allow sending messages without importing the celery tasks.
This is useful in situations like the ingest client, that may be on a remote system,
or the workflow_client.mini_response module that sends response messages from the HPC cluster,
or the UI server or jupyter notebooks that initiate control messages but do not process messages.
