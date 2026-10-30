import pytest

from datetime import datetime, timedelta

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import GetTasks, Reset, SubmitTask


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task(reset):
    result = SubmitTask(
        title='First simple task'
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())

@pytest.fixture(scope='module')
def full_task(task):
    result = SubmitTask(
        is_full=True,
        title='Second full',
        description='Some description',
        status=api.Status.InProgress,
        due_date=datetime.now() + timedelta(days=12),
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


@pytest.fixture(scope='module')
def overdue(full_task):
    result = SubmitTask(
        title='Overdue one',
        status=api.Status.InProgress,
        due_date=datetime.now() - timedelta(days=2),
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())

def test_get_tasks_empty():
    GetTasks().request().verify()


def test_get_tasks_one_talk(task):
    GetTasks().request().verify(tasks=[task])


def test_get_tasks_multiple(task, full_task):
    GetTasks().request().verify(tasks=[task, full_task])


def test_search_by_title(task, full_task, overdue):
    GetTasks(params=api.GetTasksParams.with_values({
        api.GetTasksParams.Query.name: 'First'
    })).request().verify(tasks=[task])


def test_search_by_description(task, full_task, overdue):
    GetTasks(params=api.GetTasksParams.with_values({
        api.GetTasksParams.Query.name: 'Some'
    })).request().verify(tasks=[full_task])


def test_filter_by_status(task, full_task, overdue):
    GetTasks(params=api.GetTasksParams.with_values({
        api.GetTasksParams.Status.name: api.Status.InProgress
    })).request().verify(tasks=[full_task, overdue])


def test_filter_overdue(task, full_task, overdue):
    GetTasks(params=api.GetTasksParams.with_values({
        api.GetTasksParams.Overdue.name: True
    })).request().verify(tasks=[overdue])

