import pytest
from workflow_client.nb_utils.moab_api import workflow_state_dataframe,\
    query_moab_state, combine_workflow_moab_states
from mock import patch, Mock
import pandas as pd
import io


@pytest.fixture
def task_status_dict_queued():
    return { n: 'Queued' for n in range(5, 12) }


@pytest.fixture
def task_example_dataframe_csv():
    return pd.read_csv(io.BytesIO("""
task_id,workflow_state,task_name
16,QUEUED,task_16
17,RUNNING,task_17
18,QUEUED,task_18
""".encode(encoding='utf-8')))


@pytest.fixture
def moab_example_dataframe_csv():
    return pd.read_csv(io.BytesIO("""
name,task_name,moab_state,user
5,task_5,Idle,mock_user
16,task_16,Completed,mock_user
17,task_17,Completed,mock_user
18,task_18,Completed,mock_user
""".encode(encoding='utf-8')))


@pytest.fixture
def moab_dict(task_status_dict_queued):
    user = 'mock_user'

    return [
        { 'name': k,
          'customName': 'task_%d' % (k),
          'states': { 'state': 'Complete' },
          'credentials': { 'user': user }
        } for k in task_status_dict_queued.keys()
    ]


def test_workflow_state_dataframe(task_status_dict_queued):
    df = workflow_state_dataframe(
        task_status_dict_queued)

    assert df[df['workflow_state'] != 'Queued'].empty
    assert len(df) == len(task_status_dict_queued.keys())


def test_query_moab_state(task_status_dict_queued,
                          moab_dict):
    with patch('workflow_client.nb_utils.moab_api.moab_query',
               Mock(return_value=moab_dict)) as mq:
        df = query_moab_state(
            task_status_dict_queued)

    assert len(df == len(task_status_dict_queued.keys()))
    assert df[df['moab_state'] != 'Complete'].empty
    mq.assert_called()


def test_combine(task_example_dataframe_csv,
                 moab_example_dataframe_csv):
    cd = combine_workflow_moab_states(
        task_example_dataframe_csv,
        moab_example_dataframe_csv)

    #assert str(cd) == ''
    assert cd.loc[cd.task_id.isin([16,17,18])][
        'finished_message'].all()
    assert not cd['running_message'].any()
    assert not cd['failed_message'].any()