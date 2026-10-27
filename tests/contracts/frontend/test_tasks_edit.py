import pytest
import time

from datetime import  datetime, timedelta

from surety.diff import precise_dates_equal_with_delta
from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks, wiki
from tests.contracts.utils.ui.pages.tasks import TasksPage


@pytest.fixture(scope='module', autouse=True)
def login():
    api_key = fake.password()
    LoginPage.open()
    LocalStorage.set_item(local_db.Keys.ApiKey, api_key)

    return api_key

@pytest.fixture(scope='module', autouse=True)
def load_task(login):
    task = tasks.Task(is_full=True).with_values({
        tasks.Task.DueAt.name: (
            datetime.now() + timedelta(days=1)
        ).replace(second=0, microsecond=0),
    })
    task.WikiPageId = None
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [task]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()

    return task


def test_task_loaded(load_task):
    TasksPage.TasksList.verify_tasks([load_task])


@pytest.fixture(scope='module')
def click_edit(load_task):
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: []
    }))
    tasks.GetTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        }),
        body=tasks.GetTaskResponse.with_values(load_task.value)
    )
    TasksPage.TasksList.Cards[0].EditButton.click()
    time.sleep(0.5)


def test_editing_header(load_task, click_edit):
    TasksPage.TasksList.Cards[0].EditHeader.verify_text(
        f'Editing task #{load_task.Id.value}'
    )


def test_title_edit_opened(load_task, click_edit):
    TasksPage.TasksList.Cards[0].TitleEdit.verify_value(
        load_task.Title.value
    )


@pytest.fixture(scope='module')
def new_title(click_edit):
    title = fake.sentence()
    TasksPage.TasksList.Cards[0].TitleEdit.input(title)

    return title


def test_title_changed(new_title, click_edit):
    TasksPage.TasksList.Cards[0].TitleEdit.verify_value(new_title)


@pytest.fixture(scope='module')
def cancel_changes(new_title, load_task):
    tasks.GetTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        }),
        body=tasks.GetTaskResponse.with_values(load_task.value)
    )
    TasksPage.TasksList.Cards[0].CancelButton.click()


def test_changes_canceled(cancel_changes, load_task):
    TasksPage.TasksList.verify_tasks([load_task])


@pytest.fixture(scope='module')
def edit_new_title(load_task, cancel_changes):
    tasks.GetTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        }),
        body=tasks.GetTaskResponse.with_values(load_task.value)
    )
    TasksPage.TasksList.Cards[0].EditButton.click()
    time.sleep(0.5)

    title = fake.sentence()
    TasksPage.TasksList.Cards[0].TitleEdit.input(title)

    new_task = tasks.Task.with_values(load_task.value).with_values({
        tasks.Task.Title.name: title
    })
    tasks.UpdateTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: new_task.Id.value
        }),
        body=tasks.GetTaskResponse.with_values(new_task.value),
        reset=True
    )
    tasks.GetTasks.reply(body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [new_task]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.TasksList.Cards[0].SaveButton.click()
    time.sleep(0.5)

    return title, new_task


def test_title_change_saved(edit_new_title):
    _, new_task = edit_new_title
    TasksPage.TasksList.verify_tasks([new_task])


def test_update_task_request(edit_new_title, load_task):
    title, _ = edit_new_title
    tasks.UpdateTask.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        }),
        expected=tasks.UpdateTaskRequest.with_values({
            tasks.UpdateTaskRequest.Title.name: title,
            tasks.UpdateTaskRequest.Description.name:
                load_task.Description.value,
            tasks.UpdateTaskRequest.Priority.name: load_task.Priority.value,
            tasks.UpdateTaskRequest.Status.name: load_task.Status.value,
            tasks.UpdateTaskRequest.Labels.name: load_task.Labels.value,
            tasks.UpdateTaskRequest.Assignee.name: load_task.Assignee.value,
            tasks.UpdateTaskRequest.DueAt.name: load_task.DueAt.value,
        }),
        rules={
            tasks.UpdateTaskRequest.DueAt.name: precise_dates_equal_with_delta,
        }
    )


@pytest.fixture(scope='module')
def delete_task(load_task, edit_new_title):
    tasks.DeleteTask.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        })
    )
    tasks.GetTasks.reply(body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: []
    }))
    TasksPage.TasksList.Cards[0].DeleteButton.click()


def test_task_deleted(delete_task):
    TasksPage.TasksList.verify_tasks([])


def test_delete_task(delete_task, load_task):
    tasks.DeleteTask.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value
        })
    )
