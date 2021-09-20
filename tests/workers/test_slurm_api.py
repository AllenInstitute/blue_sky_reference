import pytest
from mock import Mock, patch
from workflow_engine.process.workers.slurm_api import SlurmApi
from urllib3 import PoolManager
import json


def test_slurm_api_jobs_url():
    slurm = SlurmApi()
    url = slurm.slurm_url(table='jobs')

    assert url == 'http://slurm.corp.alleninstitute.org/api/slurm/v0.0.36/jobs'

def test_slurm_api_job_id_url():
    slurm = SlurmApi()

    url = slurm.slurm_url(table='job', oid='submit')

    assert url == 'http://slurm.corp.alleninstitute.org/api/slurm/v0.0.36/job/submit'

def test_slurm_headers():
    slurm = SlurmApi()
    headers = slurm.slurm_headers()

    assert headers['Content-Type'] == 'application/json'
    assert headers['X-SLURM-USER-NAME'] == 'TeStUsEr'
    assert headers['X-SLURM-USER-TOKEN'] == 'TeStToKeN'

def test_slurm_job_submit_payload():
    slurm = SlurmApi()
    payload = slurm.submit_job_payload(
        1234,
        '/path/to/test/script',
        "#!/usr/bin/env bash\nsleep 160"
    )

    assert 'job' in payload
    assert payload['job']['account'] == 'TeStUsEr'
    assert payload['job']['ntasks'] == 1
    assert payload['job']['cpus_per_task'] == 1
    assert payload['job']['name'] == 'task_1234'
    assert payload['job']['current_working_directory'] == '/path/to/test/script'
    assert payload['job']['time_limit'] == 600

    assert 'PATH' in payload['job']['environment']
    assert 'script' in payload

@pytest.mark.parametrize("status,expected", [(200,True), (500,False)])
def test_slurm_delete_job(status, expected):
    slurm = SlurmApi()

    mock_response = Mock()
    mock_response.status = status
    mock_request = Mock(return_value=mock_response)

    with patch.object(PoolManager, 'request', mock_request) as mr:
        result = slurm.delete_slurm_task(9876)

    assert result == expected

    mr.assert_called_with(
        'DELETE',
        'http://slurm.corp.alleninstitute.org/api/slurm/v0.0.36/job/9876',
        headers={'Content-Type': 'application/json', 'X-SLURM-USER-NAME': 'TeStUsEr', 'X-SLURM-USER-TOKEN': 'TeStToKeN'}
    )
    


def test_slurm_submit_job():
    slurm = SlurmApi()

    mock_response = Mock()
    mock_response.status = 200
    mock_response.data = json.dumps({ 'job_id': 9876 })
    mock_request = Mock(return_value=mock_response)

    with patch.object(PoolManager, 'request', mock_request) as mr:
        slurm_id = slurm.submit_job(
             1234,
             '/path/to/test/script',
             "#!/usr/bin/env bash\nsleep 160"
        )

        assert slurm_id == 9876

        mr.assert_called_with( 
            'POST',
            'http://slurm.corp.alleninstitute.org/api/slurm/v0.0.36/job/submit',
            headers={'Content-Type': 'application/json', 'X-SLURM-USER-NAME': 'TeStUsEr', 'X-SLURM-USER-TOKEN': 'TeStToKeN'},
            body=b'{"job": {"account": "TeStUsEr", "ntasks": 1, "cpus_per_task": 1, "name": "task_1234", "current_working_directory": "/path/to/test/script", "time_limit": 600, "environment": {"PATH": "/bin:/usr/bin:/usr/local/bin"}}, "script": "#!/usr/bin/env bash\\nsleep 160"}')
