import pytest
from workflow_client.nb_utils.moab_api import workflow_state_dataframe,\
    query_moab_state, combine_workflow_moab_states
from mock import patch, Mock
import pandas as pd
import io


@pytest.fixture
def task_status_dict_queued():
    return [{
        'task_id': n,
        'workflow_state': 'QUEUED',
        'moab_id': 'Moab.{}'.format(n+20)
        } for n in range(5, 12)]


@pytest.fixture
def task_example_dataframe_csv():
    return pd.read_csv(io.BytesIO("""
task_id,workflow_state,task_name,moab_id
16,QUEUED,task_16,Moab.27
17,RUNNING,task_17,Moab.28
18,QUEUED,task_18,Moab.29
""".encode(encoding='utf-8')))


@pytest.fixture
def moab_example_dataframe_csv():
    return pd.read_csv(io.BytesIO("""
name,task_name,moab_state,user,exit_code,moab_id
Moab.26,task_5,Idle,mock_user,0,Moab.26
Moab.27,task_16,Completed,mock_user,0,Moab.27
Moab.28,task_17,Completed,mock_user,0,Moab.28
Moab.29,task_18,Completed,mock_user,0,Moab.29
""".encode(encoding='utf-8')))


@pytest.fixture
def moab_dict(task_status_dict_queued):
    user = 'mock_user'

    return [
        { 'name': d['task_id'],
          'id': d['moab_id'],
          'customName': 'task_%d' % (d['task_id']),
          'states': { 'state': 'Complete' },
          'credentials': { 'user': user },
          'completionCode': 0
        } for d in task_status_dict_queued ]


def test_workflow_state_dataframe(task_status_dict_queued):
    df = workflow_state_dataframe(
        task_status_dict_queued)

    assert df[df['workflow_state'] != 'QUEUED'].empty
    assert len(df) == len(task_status_dict_queued)


def test_query_moab_state(task_status_dict_queued,
                          moab_dict):
    with patch('workflow_client.nb_utils.moab_api.moab_query',
               Mock(return_value=moab_dict)) as mq:
        df = query_moab_state(task_status_dict_queued)

    assert len(df) == len(task_status_dict_queued)
    assert df[df['moab_state'] != 'Complete'].empty
    mq.assert_called()


def test_combine(task_example_dataframe_csv,
                 moab_example_dataframe_csv):
    cd = combine_workflow_moab_states(
        task_example_dataframe_csv,
        moab_example_dataframe_csv)

    #assert str(cd) == ''
    assert cd.loc[
        cd.task_id.isin([16,17,18]),
        'finished_message'].all()
    assert not cd['running_message'].any()
    assert not cd['failed_message'].any()