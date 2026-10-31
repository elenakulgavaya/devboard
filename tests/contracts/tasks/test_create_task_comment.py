import pytest

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import (
    CreateTaskComment, Reset, SubmitTask
)


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task(reset):
    result = SubmitTask().request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


def test_create_comment_no_task():
    CreateTaskComment().request().verify(error_code=404)


def test_create_comment(task):
    CreateTaskComment(task_id=task.Id.value).request().verify()


def test_create_another_comment(task):
    CreateTaskComment(task_id=task.Id.value).request().verify()
    CreateTaskComment(task_id=task.Id.value).request().verify()

