import pytest

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


@pytest.fixture(scope='module')
def todo_task():
    return tasks.Task.with_values({
        tasks.Task.Status.name: tasks.Status.Todo
    })


@pytest.fixture(scope='module')
def overdue_task():
    return tasks.Task.with_values({
        tasks.Task.Status.name: tasks.Status.InProgress
    })


@pytest.fixture(scope='module')
def done_task():
    return tasks.Task.with_values({
        tasks.Task.Status.name: tasks.Status.Done
    })


@pytest.fixture(scope='module', autouse=True)
def load_tasks(login, todo_task, overdue_task, done_task):
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [
            todo_task, overdue_task, done_task
        ]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()


def test_all_tasks_loaded(load_tasks, todo_task, overdue_task, done_task):
    TasksPage.TasksList.verify_tasks([todo_task, overdue_task, done_task])


@pytest.fixture(scope='module')
def filter_todo(load_tasks, todo_task):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [todo_task]
    }))
    TasksPage.TodoTasks.click()


def test_tasks_filtered(filter_todo, todo_task):
    TasksPage.TasksList.verify_tasks([todo_task])


def test_filter_todo_request(filter_todo):
    tasks.GetTasks.verify_called(params={
        tasks.GetTasksParams.PageSize.name: ['100'],
        tasks.GetTasksParams.Status.name: [tasks.Status.Todo]
    })


@pytest.fixture(scope='module')
def filter_done(load_tasks, done_task):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [done_task]
    }))
    TasksPage.DoneTasks.click()


def test_tasks_filtered_done(filter_done, done_task):
    TasksPage.TasksList.verify_tasks([done_task])


def test_filter_done_request(filter_done):
    tasks.GetTasks.verify_called(params={
        tasks.GetTasksParams.PageSize.name: ['100'],
        tasks.GetTasksParams.Status.name: [tasks.Status.Done]
    })


@pytest.fixture(scope='module')
def filter_overdue(load_tasks, overdue_task):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [overdue_task]
    }))
    TasksPage.OverdueTasks.click()


def test_tasks_filtered_overdue(filter_overdue, overdue_task):
    TasksPage.TasksList.verify_tasks([overdue_task])


def test_filter_overdue_request(filter_overdue):
    tasks.GetTasks.verify_called(params={
        tasks.GetTasksParams.PageSize.name: ['100'],
        tasks.GetTasksParams.Overdue.name: ['true']
    })
