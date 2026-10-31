import pytest
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import tasks as api, wiki
from tests.contracts.utils.calls.tasks import (
    GetTask, DeleteTask, Reset, SubmitTask
)


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
    page_id = fake.random_number()
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
    )
    result = SubmitTask(
        is_full=True,
        status=api.Status.InProgress,
        priority=api.Priority.Low,
        page_id=page_id
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


def test_delete_no_task():
    DeleteTask().request().verify(error_code=404)


def test_delete_task(task):
    DeleteTask(task_id=task.Id.value).request().verify()
    GetTask(task_id=task.Id.value).request().verify(error_code=404)


def test_delete_full_task(full_task):
    DeleteTask(task_id=full_task.Id.value).request().verify()
    GetTask(task_id=full_task.Id.value).request().verify(error_code=404)
