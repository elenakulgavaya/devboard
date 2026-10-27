import pytest

from datetime import  datetime, timedelta

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks, wiki
from tests.contracts.utils.ui.pages.tasks import TasksPage


def cycle_status(task, new_status):
    updated_task = tasks.Task.with_values(task.value).with_values({
        tasks.Task.Status.name: new_status
    })
    tasks.UpdateTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: task.Id.value
        }),
        body=tasks.UpdateTaskResponse.with_values(updated_task.value),
        reset=True
    )
    tasks.GetTasks.reply(body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [updated_task]
    }))
    TasksPage.TasksList.Cards[0].StatusButton.click()

    return updated_task


@pytest.fixture(scope='module', autouse=True)
def login():
    api_key = fake.password()
    LoginPage.open()
    LocalStorage.set_item(local_db.Keys.ApiKey, api_key)

    return api_key

@pytest.fixture(scope='module', autouse=True)
def todo_task(login):
    task = tasks.Task(is_full=True).with_values({
        tasks.Task.Status.name: tasks.Status.Todo,
        tasks.Task.DueAt.name: (
            datetime.now() + timedelta(days=1)
        ).replace(second=0, microsecond=0),
    })
    task.WikiPageId = None
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [task]
    }), reset=True)
    tasks.GetTasksAssignees.reply()
    TasksPage.open()

    return task


def test_todo_task_loaded(todo_task):
    TasksPage.TasksList.verify_tasks([todo_task])


@pytest.fixture(scope='module')
def in_progress_task(todo_task):
    return cycle_status(todo_task, tasks.Status.InProgress)


def test_task_moved_to_in_progress(in_progress_task):
    TasksPage.TasksList.verify_tasks([in_progress_task])


def test_update_task_to_in_progress(in_progress_task, todo_task):
    tasks.UpdateTask.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: todo_task.Id.value
        }),
        expected=tasks.UpdateTaskStatusRequest.with_values({
            tasks.UpdateTaskStatusRequest.Status.name: tasks.Status.InProgress,
        })
    )


@pytest.fixture(scope='module')
def done_task(in_progress_task):
    return cycle_status(in_progress_task, tasks.Status.Done)


def test_task_moved_to_done(done_task):
    TasksPage.TasksList.verify_tasks([done_task])


def test_update_task_to_done(done_task, todo_task):
    tasks.UpdateTask.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: todo_task.Id.value
        }),
        expected=tasks.UpdateTaskStatusRequest.with_values({
            tasks.UpdateTaskStatusRequest.Status.name: tasks.Status.Done,
        })
    )


@pytest.fixture(scope='module')
def reopen_task(done_task):
    return cycle_status(done_task, tasks.Status.Todo)


def test_task_moved_to_todo(reopen_task):
    TasksPage.TasksList.verify_tasks([reopen_task])


def test_update_task_to_todo(reopen_task, todo_task):
    tasks.UpdateTask.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: todo_task.Id.value
        }),
        expected=tasks.UpdateTaskStatusRequest.with_values({
            tasks.UpdateTaskStatusRequest.Status.name: tasks.Status.Todo,
        })
    )
