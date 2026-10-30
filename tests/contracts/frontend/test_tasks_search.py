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
def matching_task():
    return tasks.Task()


@pytest.fixture(scope='module')
def not_matching_task():
    return tasks.Task()


@pytest.fixture(scope='module', autouse=True)
def load_tasks(login, matching_task, not_matching_task):
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [matching_task, not_matching_task]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()


def test_all_tasks_loaded(load_tasks, matching_task, not_matching_task):
    TasksPage.TasksList.verify_tasks([matching_task, not_matching_task])


@pytest.fixture(scope='module')
def search_by_title(load_tasks, matching_task, not_matching_task):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [matching_task]
    }))
    search_string = fake.sentence()
    TasksPage.SearchInput.input(search_string)
    TasksPage.TasksList.Cards.wait_for_items_load(1)

    return search_string

def test_tasks_searched(search_by_title, matching_task):
    TasksPage.TasksList.verify_tasks([matching_task])


def test_search_request(search_by_title):
    tasks.GetTasks.verify_called(params={
        tasks.GetTasksParams.PageSize.name: ['100'],
        tasks.GetTasksParams.Query.name: [search_by_title]
    })
