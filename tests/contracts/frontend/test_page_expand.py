import time

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


@pytest.fixture(scope='module', autouse=True)
def load_page(login):
    tasks.GetTasks.reply(times=2)
    tasks.GetTasksAssignees.reply()
    TasksPage.open()
    page = wiki.Page.with_values({
        wiki.Page.Content.name: '\n'.join(fake.sentence() for _ in range(10))
    })
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [page]
    }))
    TasksPage.WikiButton.click()

    return page


def test_page_loaded(load_page):
    WikiPage.PagesList.verify_pages([load_page])


@pytest.fixture(scope='module')
def expand_page(load_page):
    page_tasks = [tasks.Task.with_values({
        tasks.Task.WikiPageId.name: load_page.Id.value
    }) for _ in range(2)]
    wiki.GetPageTasks.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: load_page.Id.value
        }),
        body=wiki.GetPageTasksResponse.with_values({
            wiki.GetPageTasksResponse.Tasks.name: page_tasks
        })
    )
    WikiPage.PagesList.Cards[0].Title.click()
    time.sleep(0.5)

    return page_tasks


def test_page_expanded(expand_page, load_page):
    WikiPage.PagesList.Cards[0].verify_page(load_page, tasks=expand_page)


def test_page_tasks_requested(expand_page, load_page):
    wiki.GetPageTasks.verify_called(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: load_page.Id.value
        })
    )


@pytest.fixture(scope='module')
def collapse_page(expand_page):
    WikiPage.PagesList.Cards[0].Title.click()


def test_page_collapsed(collapse_page, load_page):
    assert WikiPage.PagesList.Cards[0].FullPage.is_not_present()
