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
def matching_page():
    return wiki.Page()


@pytest.fixture(scope='module')
def not_matching_page():
    return wiki.Page()


@pytest.fixture(scope='module', autouse=True)
def load_pages(login, matching_page, not_matching_page):
    tasks.GetTasks.reply(times=2)
    tasks.GetTasksAssignees.reply()
    TasksPage.open()
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [matching_page, not_matching_page]
    }))
    TasksPage.WikiButton.click()


def test_all_pages_loaded(load_pages, matching_page, not_matching_page):
    WikiPage.PagesList.verify_pages([matching_page, not_matching_page])


@pytest.fixture(scope='module')
def search_by_title(load_pages, matching_page, not_matching_page):
    wiki.GetPages.reply(reset=True, body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [matching_page]
    }))
    search_string = fake.sentence()
    WikiPage.SearchInput.input(search_string)
    WikiPage.PagesList.Cards.wait_for_items_load(1)

    return search_string

def test_pages_searched(search_by_title, matching_page):
    WikiPage.PagesList.verify_pages([matching_page])


def test_search_request(search_by_title):
    wiki.GetPages.verify_called(params={
        'page_size': ['100'],
        'q': [search_by_title]
    })
