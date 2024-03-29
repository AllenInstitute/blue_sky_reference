from kombu import Exchange, Queue, binding
from workflow_engine.client_settings \
    import load_settings_yaml, config_object


def configure_queues(app, name):
    workflow_engine_exchange = Exchange(name, type='direct')

    workflow_routes = [
        binding(workflow_engine_exchange, routing_key='workflow')
    ]

    moab_routes = [
        binding(workflow_engine_exchange, routing_key='moab')
    ]

    result_routes = [
        binding(workflow_engine_exchange, routing_key='result')
    ]

    null_routes = [binding(workflow_engine_exchange,
                               routing_key='null')]

    app.conf.task_queues = (
        Queue('workflow@blue_sky', workflow_routes),
        Queue('moab@blue_sky', moab_routes),
        Queue('result@blue_sky', result_routes),
        Queue('null', null_routes))


def route_task(name, args, kwargs, options, task=None, **kw):
    task_name = '.'.split(name)[-1]
    if task_name in {
        'check_moab_status',
        'submit_moab_task',
        'submit_job',
        'kill_moab_task',
        'run_task' }:
        return { 
            'queue': 'moab@blue_sky' }
    elif task_name in {
        'create_job',
        'queue_job',
        'enqueue_next_queue',
        'run_workflow_node_jobs_by_id' }:
        return { 'queue': 'workflow@blue_sky' }
    elif task_name in [ 
        'process_pbs_id,'
        'process_running',
        'process_failed_execution',
        'process_finished_execution' ]:
        return { 'queue': 'result@blue_sky' }
    else:
        return { 'queue': 'null' }


def configure_combined_app(app, app_name):
    settings = load_settings_yaml()
    app.config_from_object(config_object(settings))

    configure_queues(app, app_name)
    app.conf.task_routes = [route_task]
