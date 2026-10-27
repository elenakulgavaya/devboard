import time

import pytest
from surety.diff import compare

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
def pages(login):
    return [wiki.Page() for i in range(4)]


@pytest.fixture(scope='module')
def linked_task(pages):
    return tasks.Task.with_values({
        tasks.Task.WikiPageId.name: pages[0].Id.value
    })


@pytest.fixture(scope='module', autouse=True)
def tasks_page(login, pages, linked_task):
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [linked_task]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()


@pytest.fixture(scope='module')
def click_new_task(pages):
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: pages
    }))
    TasksPage.NewTaskButton.click()


def test_available_pages(click_new_task, pages):
    compare(
        actual=TasksPage.NewTask.WikiPage.all_options,
        expected=['No wiki page'] + [page.Title.value for page in pages],
    )


def test_task_is_linked(click_new_task, linked_task, tasks_page):
    TasksPage.TasksList.verify_tasks([linked_task])



@pytest.fixture(scope='module')
def click_wiki_badge(click_new_task, linked_task, pages):
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [pages[0]]
    }))
    TasksPage.TasksList.Cards[0].WikiBadge.click()
    time.sleep(0.5)


def test_page_opened(click_wiki_badge, linked_task, pages):
    WikiPage.PagesList.verify_pages([pages[0]], is_full=True)
