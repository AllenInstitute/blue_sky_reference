import pytest
from mock import Mock, patch, MagicMock
from workflow_engine.models.workflow import Workflow
from workflow_engine.workflow_controller import WorkflowController
from workflow_engine.strategies.ingest_strategy \
    import IngestStrategy

@pytest.fixture
def in_strat():
    return IngestStrategy()


def test_get_workflow_name(in_strat):
    default_name = in_strat.get_workflow_name()

    assert default_name is None


def test_skip_execution(in_strat):
    enqueued_object = Mock()

    skip = in_strat.skip_execution(enqueued_object)
    
    assert skip is True


def test_create_enqueued_object(in_strat):
    dictionary = Mock()

    default_obj = in_strat.create_enqueued_object(dictionary)
    
    assert default_obj is None


def test_generate_response(in_strat):
    enqueued_object = Mock()

    default_response = in_strat.generate_response(enqueued_object)
    
    assert default_response is None


def test_is_ingest_strategy(in_strat):
    is_ingest = in_strat.is_ingest_strategy()
    
    assert is_ingest is True


@pytest.mark.django_db
def test_ingest_message(in_strat):
    message = Mock()
    tags = ['a', 'b']

    with patch.object(WorkflowController, 'start_workflow'):
        in_strat.ingest_message(message, tags)


@pytest.mark.django_db
def test_ingest_message_no_tags(in_strat):
    message = Mock()

    with patch.object(WorkflowController, 'start_workflow'):
        in_strat.ingest_message(message)


# TODO: remove hardcoded model
@pytest.mark.django_db
def test_ingest_message_HARDCODED(in_strat):
    message = Mock()

    with patch.object(WorkflowController, 'start_workflow'):
        in_strat.ingest_message(message, tags='ReferenceSet')


def test_run_task(in_strat):
    task = Mock()

    in_strat.run_task(task)


def test_finish_task(in_strat):
    task = Mock()

    in_strat.finish_task(task)


def test_call_ingest_strategy():
    wf_name = 'test_workflow_name'
    msg = 'test_message'
    
    with patch('workflow_engine.models.workflow.Workflow.objects.get'):
        with patch('workflow_engine.strategies.ingest_strategy.import_class',
                   MagicMock()):
            IngestStrategy.call_ingest_strategy(wf_name, msg)
