import pytest

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import UpdateTask, Reset, SubmitTask


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task(reset):
    result = SubmitTask(
        status=api.Status.Todo
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())

@pytest.fixture(scope='module')
def full_task(task):
    result = SubmitTask(
        is_full=True,
        status=api.Status.InProgress,
        priority=api.Priority.Low
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


def test_update_no_task():
    UpdateTask().request().verify(error_code=404)


def test_update_task_no_changes(task):
    UpdateTask(task_id=task.Id.value).request().verify(task=task)


def test_update_task_status(task):
    UpdateTask(
        task_id=task.Id.value,
        body=api.UpdateTaskRequest.with_values({
            api.UpdateTaskRequest.Status.name: api.Status.InProgress,
        })
    ).request().verify(task=task)


def test_update_task_full(task):
    UpdateTask(
        task_id=task.Id.value,
        body=api.UpdateTaskRequest(is_full=True)
    ).request().verify(task=task)


def test_update_full_task_rewrite(full_task):
    UpdateTask(
        task_id=full_task.Id.value,
        body=api.UpdateTaskRequest(is_full=True)
    ).request().verify(task=full_task)
