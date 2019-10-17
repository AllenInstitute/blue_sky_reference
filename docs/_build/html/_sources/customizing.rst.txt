Customization
=============

This guide is a resource for extending the Blue Sky Workflow Engine package
in the context of creating a production workflow.


Blue Sky Reference Application
------------------------------

The blue sky reference app is a small project that serves several purposes.
It contains the unit and integration tests for the workflow engine as well
as code analysis (linting and coverage), as well as documentation. It also
provides a small working application that illustrates many of the ways
the workflow engine's components can be extended without the real-world
complexity of a production application.

The reference application may be found in the
`AllenInstitute/blue_sky_reference <https://github.com/AllenInstitute/blue_sky_reference>`
github repository.

Creating a Model
----------------

Application models inherit from Django's :class:`model.Model`.

The :class:`workflow_engine.mixins` package contains reusable code that
many models will need.

Models that are to be passed to a :term:`Strategy` as an :term:`enqueueable object`
should mix in :class:`~workflow_engine.mixins.enqueueable.Enqueueable`

Models can mixin :class:`~workflow_engine.mixins.stateful.Stateful` in order to
make use of the `django_fsm <https://github.com/viewflow/django-fsm>`_ :term:`finite state machine` package to
track an :term:`object state` distinct from the :term:`workflow state`.

Models that may be archived should use the archivable mixin,
this will also provide a model manager that will filter out archived
instances by default.

Models that will have :term:`well known file` or :term:`configuration` objects
attached should mixin :class:`~workflow_engine.mixins.has_well_known_files.HasWellKnownFiles`
or :class:`~workflow_engine.mixins.configurable.Configurable`

Models with human-readable names and descriptions
should mixin :class:`~workflow_engine.mixins.nameable.Nameable`

Some of the mixins such as :class:`~workflow_engine.mixins.runnable.Runnable`
are intended for internal workflow_engine models.


Creating Strategies
-------------------

A workflow :term:`strategy` is a translation layer from a database query and
an operation performed in a workflow node. There are four main types of strategies.

An :class:`~workflow_engine.strategies.execution_strategy.ExecutionStrategy`
is used to create input and parse output JSON files to pass to
modules that are run as tasks on a compute cluster.
Override :func:`~workflow_engine.strategies.execution_strategy.ExecutionStrategy.get_input`
to create the input JSON file,
and :func:`~workflow_engine.strategies.base_strategy.BaseStrategy.on_finishing`
to process the output JSON file.

The input file is generated and the output file is checked by the workflow engine,
but when it is necessary to avoid touching the filesystem,
override :func:`~workflow_engine.strategies.execution_strategy.ExecutionStrategy.get_input_file` 
and :func:`~workflow_engine.strategies.execution_strategy.ExecutionStrategy.get_output_file` 
to return None. This feature can be used during testing or to implement
message-only communication with the worklow worker process.
See :class:`~blue_sky.strategies.mock_execution_strategy.MockExecutionStrategy`
for an example of this technique.

The mixin :class:`~workflow_engine.strategies.input_config_mixin.InputConfigMixin`
can be used to read an initial input JSON from 
a :class:`~workflow_engine.models.configuration.Configuration`

To change the type of :term:`enqueued object` from one :term:`workflow node`
to the next, override 
:func:`~workflow_engine.strategies.base_strategy.BaseStrategy.transform_objects_for_queue`
This can be used flexibly to implement workflow nodes that collect workflow nodes
into an associated group. Or it may be used to hold enqueued objects until an
associated object has finished processing in a different branch of the workflow.
:func:`blue_sky.strategies.mock_analyze.MockAnalyze.transform_objects_for_queue`
is a demonstration of this technique.

If the enqueued object to be tracked as a job in the workflow differs from the enqueued
object sent as a task to the compute cluster,
overriding :func:`~workflow_engine.strategies.base_strategy.BaseStrategy.get_task_objects_for_queue`
can control the mapping. Note that the workflow has more flexibility for handling jobs
than tasks, so the default of one task per job is recommended.
The use of :class:`~blue_sky.models.observation_group.ObservationGroup`
and :class:`~blue_sky.models.group_assignment.GroupAssignment`
in the :class:`~blue_sky.strategies.mock_process_grouped_observations.MockProcessGroupedObservations`
strategy is an example of how to process a group of jobs rather than using multiple tasks per job.

A :class:`~workflow_engine.strategies.wait_strategy.WaitStrategy` can be used
to temporarily suspend the progression of an :term:`enqueued object` through a
:term:`workflow`. This model is deprecated because the same functionality can
be implemented by overriding :func:`~workflow_engine.strategies.base_strategy.BaseStrategy.must_wait`
to return True. This may be used to wait for a manual update (often an update to
the :term:`object state` of a model that uses the
:class:`~workflow_engine.mixins.stateful.Stateful` mixin).
It may also be used to wait for an automatic trigger, such as a transition in
the :term:`workflow state` and/or :term:`object state` of an associated object.
:func:`blue_sky.strategies.mock_analyze.MockAnalyze.must_wait` is an
illustration of this technique.

An :class:`~workflow_engine.strategies.ingest_strategy.IngestStrategy` may be
used to receive celery messages from outside the workflow. It is intended to
create new databased objects using Django models and then enqueueing them at
the start of a :term:`workflow`.
Override :func:`~workflow_engine.strategies.ingest_strategy.IngestStrategy.create_enqueued_object`
to parse the ingest message and update the database.
Override :func:`~workflow_engine.strategies.ingest_strategy.IngestStrategy.generate_response`
to serialize the body of a response message to return to the ingest message sender.
:class:`blue_sky.strategies.mock_ingest.MockIngest` is an illustration of an
ingest strategy. Note that an ingest strategy is only one technique for
creating model objects. For development or other reasons, a Django management command,
a `Django shell_plus <https://django-extensions.readthedocs.io/en/latest/shell_plus.html>`_
script or notebook,
a custom `Django view <https://docs.djangoproject.com/en/2.2/topics/http/views/>`_
or an `admin action <https://docs.djangoproject.com/en/2.2/ref/contrib/admin/actions/>`_ could all create an object
and then enqueue it.

Creating a Workflow
-------------------

A :term:`workflow` is built up from a set of :class:`~workflow_engine.models.workflow_node.WorkflowNode`
objects connected by :class`~workflow_engine.models.workflow_edge.WorkflowEdge`
connections in the form of a :term:`directed acyclic graph` (DAG). Note that the
workflow engine does not currently implement checks for cycles, but the workflow
can be inspected visually in the workflow list view of the admin console.

Each :class:`~workflow_engine.models.workflow_node.WorkflowNode` is associated
with a :class:`~workflow_engine.models.job_queue.JobQueue` which in turn is
associated with a :term:`strategy`
and an :class:`~workflow_engine.models.executable.Executable`.

The :class:`~workflow_engine.workflow_controller.WorkflowController` takes
:term:`enqueued objects` off the job queues in batches. An enqueued_object in
a particular job queue is represented by a :class:`~workflow_engine.models.job.Job`
object, which is processed through a strategy to create and process input parameters
and output parameters and update the enqueued object state. 
One or more :class:`~workflow_engine.models.task.Task` objects and the executable
are then used to create a script to submit to the remote worker on a compute cluster
or other remote system.

A workflow may be defined in a `YAML <https://yaml.org/>`_ syntax that can be
parsed by the :class:`~workflow_engine.workflow_config.WorkflowConfig`.
The syntax is described in more detail on the :ref:`workflows` page.

The :class:`workflow_engine.management.commands.import_workflows`
`custom Django management command <https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/>`_
may be used to read in a workflow_configuration.yml.
There is an example in the config direcory of the reference application::

    python -m workflow_engine.management.manage import_workflows blue_sky/config/workflow_config.yml

Note that the $DJANGO_SETTINGS_MODULE must be properly set for this command to find the database.

Customizing the Admin UI
------------------------

Some activities are easier to implement as a standard web list view or detail view.
For this the`Django Admin Plugin <https://docs.djangoproject.com/en/2.2/ref/contrib/admin/>`_
is useful.  The workflow engine has several customized admin classes, incluging the
:class:`~workflow_engine.admin.job_admin.JobAdmin` and :class:`~workflow_engine.admin.job_admin.JobAdmin`.
The :class:`~workflow_engine.admin.workflow_admin.WorkflowAdmin` includes a user interface view
that draws the graph of active workflows.

The admin console may be used to hand-edit workflows during development.
It is possible to create executables, job_queues, workflow nodes, connect them with
edges and attach them to workflows using the admin views.

It is also possible to filter workflow objects and run actions such as killing or
starting a job using the admin console. Default functionality includew sorting and paging.

The reference application has exmaples of how to customize the behavior and
available actions of the admin console for application models.
:class:`blue_sky.admin.observation_group_admin.ObservationGroupAdmin` shows
how simple it is to specify which columns to display, how to add a filter
and how to add an action in a few lines of code.