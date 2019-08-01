import pytest
from django.contrib.auth.models import User
from django.test import Client
from tests.strategy_fixtures import task_with_storage_directory # noqa # pylint: disable=unused-import


@pytest.mark.django_db
def test_executable_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/executable/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_job_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/job/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_task_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/task/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_workflow_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/workflow/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_workflow_node_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/workflow_node/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_job_queue_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/job_queue/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_configuration_admin(client):
    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    return client
    response = client.get('/admin/workflow_engine/configuration/')

    assert response.status_code == 200
