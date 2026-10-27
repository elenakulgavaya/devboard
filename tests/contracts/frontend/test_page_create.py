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
def wiki_page(login):
    tasks.GetTasks.reply(times=2)
    tasks.GetTasksAssignees.reply()
    TasksPage.open()
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: []
    }))
    TasksPage.WikiButton.click()


def test_new_page_form_is_closed(wiki_page):
    assert WikiPage.NewPage.is_not_present()


@pytest.fixture(scope='module')
def click_new_page(wiki_page):
    WikiPage.NewPageButton.click()


def test_new_page_button_opens_form(click_new_page):
    WikiPage.NewPage.wait_for_load()


@pytest.fixture(scope='module')
def click_cancel(click_new_page):
    WikiPage.NewPage.CancelButton.click()
#

def test_cancel_button_closes_page_form(click_cancel):
    WikiPage.NewPage.wait_for_not_present()


@pytest.fixture(scope='module')
def submit_empty(click_cancel):
    WikiPage.NewPageButton.click()
    WikiPage.NewPage.SaveButton.click()


def test_create_page_requires_title(submit_empty):
    WikiPage.NewPage.TitleError.verify_text('Title is required')


def test_create_page_no_title_form_remains_open(submit_empty):
    assert WikiPage.NewPage.is_present()


@pytest.fixture(scope='module')
def enter_title(submit_empty):
    title = fake.sentence()
    WikiPage.NewPage.Title.input(title)
    return title


def test_title_value(enter_title):
    WikiPage.NewPage.Title.verify_value(enter_title)


@pytest.fixture(scope='module')
def submit_title(enter_title):
    new_page = wiki.Page.with_values({
        wiki.Page.Title.name: enter_title,
    })
    wiki.CreateNewPage.reply(
        body=wiki.CreateNewPageResponse.with_values(new_page.value),
        reset=True
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [new_page]
    }))
    WikiPage.NewPage.SaveButton.click()

    return new_page


def test_new_page_form_closed(submit_title):
    assert WikiPage.NewPage.is_not_present()


def test_create_page_request(submit_title, enter_title):
    wiki.CreateNewPage.verify_called(
        expected=wiki.CreateNewPageRequest.with_values({
            wiki.CreateNewPageRequest.Title.name: enter_title,
        })
    )

def test_new_page_in_the_list(submit_title):
    WikiPage.PagesList.verify_pages([submit_title])


@pytest.fixture(scope='module')
def add_another(submit_title):
    WikiPage.NewPageButton.click()


def test_title_reset(add_another):
    WikiPage.NewPage.Title.verify_value('')


@pytest.fixture(scope='module')
def new_title(add_another):
    title = fake.sentence()
    WikiPage.NewPage.Title.input(title)

    return title


def test_new_title(new_title):
    WikiPage.NewPage.Title.verify_value(new_title)


@pytest.fixture(scope='module')
def content(new_title):
    new_content = fake.sentence()
    WikiPage.NewPage.Content.input(new_content)

    return new_content


def test_content(content):
    WikiPage.NewPage.Content.verify_value(content)


@pytest.fixture(scope='module')
def submit_full(submit_title, new_title, content):
    new_page = wiki.Page.with_values({
        wiki.Page.Title.name: new_title,
        wiki.Page.Content.name: content,
    })
    wiki.CreateNewPage.reply(
        body=wiki.CreateNewPageResponse.with_values(new_page.value),
        reset=True
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [submit_title, new_page]
    }))
    WikiPage.NewPage.SaveButton.click()

    return new_page


def test_create_page_full_request(submit_full, new_title, content):
    wiki.CreateNewPage.verify_called(
        expected=wiki.CreateNewPageRequest.with_values({
            wiki.CreateNewPageRequest.Title.name: new_title,
            wiki.CreateNewPageRequest.Content.name: content,
        }), timeout=2
    )


def test_new_full_page_in_the_list(submit_title, submit_full):
    WikiPage.PagesList.verify_pages([submit_title, submit_full])


@pytest.fixture(scope='module')
def reopen_new_page_form(submit_full):
    WikiPage.NewPageButton.click()


def test_page_title_is_cleared(reopen_new_page_form):
    WikiPage.NewPage.Title.verify_value('')


def test_content_is_cleared(reopen_new_page_form):
    WikiPage.NewPage.Content.verify_value('')
