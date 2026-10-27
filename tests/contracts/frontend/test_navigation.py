import pytest

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks, wiki
from tests.contracts.utils.ui.pages.tasks import TasksPage
from tests.contracts.utils.ui.pages.wiki import WikiPage


@pytest.fixture(scope='module', autouse=True)
def login():
    api_key = fake.password()
    LoginPage.open()
    LocalStorage.set_item(local_db.Keys.ApiKey, api_key)

    return api_key


@pytest.fixture(scope='module')
def load_tasks(login):
    loaded_tasks = [tasks.Task() for _ in range(3)]
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: loaded_tasks
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()

    return loaded_tasks


def test_all_tasks_loaded(load_tasks):
    TasksPage.TasksList.verify_tasks(load_tasks)


@pytest.fixture(scope='module')
def go_to_wiki(load_tasks):
    pages = [wiki.Page() for _ in range(3)]
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: pages
    }))
    TasksPage.WikiButton.click()

    return pages


def test_wiki_loaded(go_to_wiki):
    WikiPage.PagesList.verify_pages(go_to_wiki)


@pytest.fixture(scope='module')
def go_to_tasks(go_to_wiki):
    new_tasks = [tasks.Task() for _ in range(3)]
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: new_tasks
    }))
    WikiPage.TasksButton.click()

    return new_tasks


def test_tasks_page_reloaded(go_to_tasks):
    TasksPage.TasksList.verify_tasks(go_to_tasks)
