import pytest
from workflow_engine.worker.qsub.qsub_api \
    import query_qstat_moab_state, parse_qstat_full_output,\
    query_and_combine_qstat_states
from mock import patch, Mock
import pandas as pd
import io

_QSTAT_FULL_OUTPUT = """
Job Id: 6293199.qmaster2.corp.alleninstitute.org
    Job_Name = task_52908
    Job_Owner = mock_svc_vol_assem@qmaster2.corp.alleninst.org
    resources_used.cput = 00:01:06
    resources_used.energy_used = 0
    resources_used.mem = 5360756kb
    resources_used.vmem = 44628168kb
    resources_used.walltime = 00:01:20
    job_state = R
    queue = celltypes
    server = qmaster2.corp.alleninst.org
    Checkpoint = u
    ctime = Tue Aug 14 17:18:10 2018
    Error_Path = qmaster2.corp.alleninst.org:/allen/programs/celltypes/product
    ion/wijem/workflow_data/production/4757/jobs/job_55540/tasks/task_5290
    8/log_52908.txt
    exec_host = n137/0
    Hold_Types = n
    Join_Path = oe
    Keep_Files = n
    Mail_Points = a
    mtime = Tue Aug 14 17:18:16 2018
    Output_Path = qmaster2.corp.alleninst.org:/allen/programs/celltypes/produc
    tion/wijem/workflow_data/production/4757/jobs/job_55540/tasks/task_529
    08/log_52908.txt
    Priority = 0
    qtime = Tue Aug 14 17:18:10 2018
    Rerunable = False
    Resource_List.partition = [pbs][mws]
    Resource_List.feature = centos
    Resource_List.mem = 40gb
    Resource_List.nodes = 1:ppn=1
    Resource_List.walltime = 04:00:00
    Resource_List.nodect = 1
    session_id = 16175
    euser = mock_svc_vol_assem
    egroup = domain_users
    queue_type = E
    etime = Tue Aug 14 17:18:10 2018
    start_time = Tue Aug 14 17:18:16 2018
    Walltime.Remaining = 14266
    start_count = 1
    fault_tolerant = False
    job_radix = 0
    submit_host = qmaster2.corp.alleninst.org
    init_work_dir = /home/svc_vol_assem
    request_version = 1
    req_information.task_count.0 = 1
    req_information.lprocs.0 = 1
    req_information.memory.0 = 41943040kb
    req_information.thread_usage_policy.0 = allowthreads
    req_information.hostlist.0 = n137:ppn=1
    req_information.task_usage.0.task.0.cpu_list = 0
    req_information.task_usage.0.task.0.mem_list = 0
    req_information.task_usage.0.task.0.cores = 0
    req_information.task_usage.0.task.0.threads = 1
    req_information.task_usage.0.task.0.host = n137
    x = SID:Moab;SJID:Moab.83521;SRMJID:Moab.83521
    cpuset_string = n137:0
    memset_string = n137:0

Job Id: 6293200.qmaster2.corp.alleninstitute.org
    Job_Name = task_53087
    Job_Owner = mock_svc_vol_assem@qmaster2.corp.alleninst.org
    resources_used.cput = 00:00:46
    resources_used.energy_used = 0
    resources_used.mem = 4126532kb
    resources_used.vmem = 44628240kb
    resources_used.walltime = 00:01:00
    job_state = R
    queue = celltypes
    server = qmaster2.corp.alleninst.org
    Checkpoint = u
    ctime = Tue Aug 14 17:18:11 2018
    Error_Path = qmaster2.corp.alleninst.org:/allen/programs/celltypes/product
    ion/wijem/workflow_data/production/4761/jobs/job_55246/tasks/task_5308
    7/log_53087.txt
    exec_host = n120/0
    Hold_Types = n
    Join_Path = oe
    Keep_Files = n
    Mail_Points = a
    mtime = Tue Aug 14 17:18:16 2018
    Output_Path = qmaster2.corp.alleninst.org:/allen/programs/celltypes/produc
    tion/wijem/workflow_data/production/4761/jobs/job_55246/tasks/task_530
    87/log_53087.txt
    Priority = 0
    qtime = Tue Aug 14 17:18:11 2018
    Rerunable = False
    Resource_List.partition = [pbs][mws]
    Resource_List.feature = centos
    Resource_List.mem = 40gb
    Resource_List.nodes = 1:ppn=1
    Resource_List.walltime = 04:00:00
    Resource_List.nodect = 1
    session_id = 15422
    euser = mock_svc_vol_assem
    egroup = domain_users
    queue_type = E
    etime = Tue Aug 14 17:18:11 2018
    start_time = Tue Aug 14 17:18:16 2018
    Walltime.Remaining = 14266
    start_count = 1
    fault_tolerant = False
    job_radix = 0
    submit_host = qmaster2.corp.alleninst.org
    init_work_dir = /home/svc_vol_assem
    request_version = 1
    req_information.task_count.0 = 1
    req_information.lprocs.0 = 1
    req_information.memory.0 = 41943040kb
    req_information.thread_usage_policy.0 = allowthreads
    req_information.hostlist.0 = n120:ppn=1
    req_information.task_usage.0.task.0.cpu_list = 0
    req_information.task_usage.0.task.0.mem_list = 0
    req_information.task_usage.0.task.0.cores = 0
    req_information.task_usage.0.task.0.threads = 1
    req_information.task_usage.0.task.0.host = n120
    x = SID:Moab;SJID:Moab.83522;SRMJID:Moab.83522
    cpuset_string = n120:0
    memset_string = n120:0
"""

# @pytest.fixture
# def task_status_dict_queued():
#     return [{
#         'task_id': n,
#         'workflow_state': 'QUEUED',
#         'moab_id': 'Moab.{}'.format(n+20)
#         } for n in range(5, 12)]
# 
# 
# @pytest.fixture
# def task_example_dataframe_csv():
#     return pd.read_csv(io.BytesIO("""
# task_id,workflow_state,task_name,moab_id
# 16,QUEUED,task_16,Moab.27
# 17,RUNNING,task_17,Moab.28
# 18,QUEUED,task_18,Moab.29
# """.encode(encoding='utf-8')))
# 
# 
# @pytest.fixture
# def moab_example_dataframe_csv():
#     return pd.read_csv(io.BytesIO("""
# name,task_name,moab_state,user,exit_code,moab_id
# Moab.26,task_5,Idle,mock_user,0,Moab.26
# Moab.27,task_16,Completed,mock_user,0,Moab.27
# Moab.28,task_17,Completed,mock_user,0,Moab.28
# Moab.29,task_18,Completed,mock_user,0,Moab.29
# """.encode(encoding='utf-8')))
# 
# 
# @pytest.fixture
# def moab_dict(task_status_dict_queued):
#     user = 'mock_user'
# 
#     return [
#         { 'name': d['task_id'],
#           'id': d['moab_id'],
#           'customName': 'task_%d' % (d['task_id']),
#           'states': { 'state': 'Complete' },
#           'credentials': { 'user': user },
#           'completionCode': 0
#         } for d in task_status_dict_queued ]
# 
# 
# def test_workflow_state_dataframe(task_status_dict_queued):
#     df = workflow_state_dataframe(
#         task_status_dict_queued)
# 
#     assert df[df['workflow_state'] != 'QUEUED'].empty
#     assert len(df) == len(task_status_dict_queued)
# 
_WORKFLOW_STATE_DICTS = {}
_MOCK_USER = 'svc_vol_assem'

@pytest.fixture
def workflow_state_dicts():
    return _WORKFLOW_STATE_DICTS


@pytest.fixture
def task_qstat_dict():
    return [{
        'task_id': n,
        'workflow_state': 'QUEUED',
        'moab_id': 'Moab.{}'.format(n+20)
        } for n in range(5, 12)]

@pytest.fixture
def mock_user():
    return _MOCK_USER


@pytest.fixture
def mock_qstat_query(mock_user, task_qstat_dict):
    return mock_qstat_query_helper(mock_user, task_qstat_dict)

def mock_qstat_query_helper(mock_user, task_qstat_dict):
    mock_moab_dict_array = [{
            'name': str(i),
            'id': '9876543{}.qmaster2.alleninstitute.org'.format(i),
            'customName': 'task_{}'.format (i),
            'states': { 'state': 'Complete' },
            'credentials': { 'user': mock_user },
            'completionCode': 0
        } for i in [x+10*x for x in range(0, 25)]]

    return Mock(return_value=mock_moab_dict_array)


def test_parse_qstat_full_output():
    with io.StringIO(_QSTAT_FULL_OUTPUT) as f:
        moab_state_dict = parse_qstat_full_output(
            f.readlines())

    assert moab_state_dict is not None


@patch('workflow_engine.worker.qsub.qsub_api.qstat_query',
       mock_qstat_query_helper(_MOCK_USER, _WORKFLOW_STATE_DICTS))
def test_query_qstat_moab_state(mock_user, workflow_state_dicts):
    moab_state_df = query_qstat_moab_state(workflow_state_dicts)

    assert moab_state_df is not None
    # assert str(moab_state_df.to_json(orient='records')) == ''


@patch('workflow_engine.worker.qsub.qsub_api.qstat_query',
       mock_qstat_query_helper(_MOCK_USER, _WORKFLOW_STATE_DICTS))
def test_query_and_combine_qstat_states(
    mock_user, workflow_state_dicts):
    combined_df = query_and_combine_qstat_states(
        workflow_state_dicts)

    assert combined_df is not None
    # assert str(combined_df) == ''

# def test_query_moab_state(task_status_dict_queued,
#                           moab_dict):
#     with patch('workflow_client.nb_utils.moab_api.moab_query',
#                Mock(return_value=moab_dict)) as mq:
#         df = query_moab_state(task_status_dict_queued)
# 
#     assert len(df) == len(task_status_dict_queued)
#     assert df[df['moab_state'] != 'Complete'].empty
#     mq.assert_called()
# 
# 
# def test_combine(task_example_dataframe_csv,
#                  moab_example_dataframe_csv):
#     cd = combine_workflow_moab_states(
#         task_example_dataframe_csv,
#         moab_example_dataframe_csv)
# 
#     #assert str(cd) == ''
#     assert cd.loc[
#         cd.task_id.isin([16,17,18]),
#         'finished_message'].all()
#     assert not cd['running_message'].any()
#     assert not cd['failed_message'].any()
