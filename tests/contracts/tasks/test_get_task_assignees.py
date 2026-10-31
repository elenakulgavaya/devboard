import pytest

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import (
    GetTasksAssignees, Reset, SubmitTask
)


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task(reset):
    result = SubmitTask(is_full=True).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())

@pytest.fixture(scope='module')
def another_task(task):
    result = SubmitTask(is_full=True).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


def test_get_assignees_no_tasks():
    GetTasksAssignees().request().verify()


def test_get_single_assignee(task):
    GetTasksAssignees().request().verify(assignees=[task.Assignee.value])


def test_get_multiple_assignees(task, another_task):
    GetTasksAssignees().request().verify(
        assignees=[task.Assignee.value, another_task.Assignee.value]
    )
