import pytest
from mock import Mock

@pytest.fixture
def task_with_storage_directory():
    task = Mock()
    task.id = 123456

    enqueued_obj = Mock()
    enqueued_obj.id = 555
    enqueued_obj.get_storage_directory = Mock(
        return_value='/path/to/storage/mock_enqueued_object/10'
    )#         return_value='/path/to/base_storage/directory')

    task.job = Mock()
    task.job.id = 789
    task.job.enqueued_object_type = 'mock_model'
    task.job.enqueued_object_type = enqueued_obj.id
    task.job.enqueued_object = enqueued_obj
    task.job.get_or_create_task_storage_directory = Mock(
        return_value='/path/to/task/storage'
    )

    mock_executable = Mock()
    mock_executable.pbs_executable_path = 'mock.exe'
    mock_executable.static_arguments = '-mock_static mock_arguments'

    task.workflow_node = Mock()
    task.workflow_node.job_queue = Mock()
    task.workflow_node.job_queue.executable = mock_executable
    task.get_executable = Mock(return_value=mock_executable)

    return task
