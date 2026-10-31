import pytest
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import (
    GetTaskHistory, UpdateTask, Reset, SubmitTask
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
def updated_status_task(task):
    result = SubmitTask(
        status=api.Status.InProgress,
    ).request().verify_response(error_code=201)
    task = api.Task().with_values(result.response.json())
    _result = UpdateTask(
        task_id=task.Id.value,
        body=api.UpdateTaskRequest.with_values({
            api.UpdateTaskRequest.Status.name: api.Status.Done,
        })
    ).request().verify_response()
    task = api.Task().with_values(_result.response.json())

    return task, [api.HistoryEntry.with_values({
        api.HistoryEntry.Id.name: 1,
        api.HistoryEntry.TaskId.name: task.Id.value,
        api.HistoryEntry.Field.name: api.Task.Status.name,
        api.HistoryEntry.OldValue.name: api.Status.InProgress,
        api.HistoryEntry.NewValue.name: api.Status.Done,
        api.HistoryEntry.ChangedAt.name: task.UpdatedAt.value,
    })]


@pytest.fixture(scope='module')
def updated_two_fields_task(task):
    result = SubmitTask(
        priority=api.Priority.High,
    ).request().verify_response(error_code=201)
    task = api.Task().with_values(result.response.json())
    _result = UpdateTask(
        task_id=task.Id.value,
        body=api.UpdateTaskRequest.with_values({
            api.UpdateTaskRequest.Priority.name: api.Priority.Low,
            api.UpdateTaskRequest.Assignee.name: fake.name(),
        })
    ).request().verify_response()
    task = api.Task().with_values(_result.response.json())

    return task, [
        api.HistoryEntry.with_values({
            api.HistoryEntry.Id.name: 2,
            api.HistoryEntry.TaskId.name: task.Id.value,
            api.HistoryEntry.Field.name: api.Task.Assignee.name,
            api.HistoryEntry.OldValue.name: None,
            api.HistoryEntry.NewValue.name: task.Assignee.value,
            api.HistoryEntry.ChangedAt.name: task.UpdatedAt.value,
        }),
        api.HistoryEntry.with_values({
            api.HistoryEntry.Id.name: 3,
            api.HistoryEntry.TaskId.name: task.Id.value,
            api.HistoryEntry.Field.name: api.Task.Priority.name,
            api.HistoryEntry.OldValue.name: api.Priority.High,
            api.HistoryEntry.NewValue.name: api.Priority.Low,
            api.HistoryEntry.ChangedAt.name: task.UpdatedAt.value,
        })
    ]

def test_get_history_no_task():
    GetTaskHistory().request().verify(error_code=404)


def test_get_history_no_updates(task):
    GetTaskHistory(task_id=task.Id.value).request().verify()


def test_get_history_one_update(updated_status_task):
    task, history = updated_status_task
    GetTaskHistory(task_id=task.Id.value).request().verify(history=history)


def test_get_history_multi_update(updated_two_fields_task):
    task, history = updated_two_fields_task
    GetTaskHistory(task_id=task.Id.value).request().verify(history=history)
