import pytest
import time

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
    loaded_page = wiki.Page()
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [loaded_page]
    }))
    TasksPage.WikiButton.click()

    return loaded_page

def test_wiki_page_loaded(wiki_page):
    WikiPage.PagesList.verify_pages([wiki_page])


@pytest.fixture(scope='module')
def click_edit(wiki_page):
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        }),
        body=wiki.GetPageResponse.with_values(wiki_page.value)
    )
    WikiPage.PagesList.Cards[0].EditButton.click()
    time.sleep(0.5)


def test_page_editing_header(wiki_page, click_edit):
    WikiPage.PagesList.Cards[0].EditHeader.verify_text(
        f'Editing page #{wiki_page.Id.value}'
    )


def test_title_edit_opened(wiki_page, click_edit):
    WikiPage.PagesList.Cards[0].TitleEdit.verify_value(wiki_page.Title.value)


@pytest.fixture(scope='module')
def new_title(click_edit):
    title = fake.sentence()
    WikiPage.PagesList.Cards[0].TitleEdit.input(title)

    return title


def test_page_title_changed(new_title, click_edit):
    WikiPage.PagesList.Cards[0].TitleEdit.verify_value(new_title)


@pytest.fixture(scope='module')
def cancel_changes(new_title, wiki_page):
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        }),
        body=wiki.GetPageResponse.with_values(wiki_page.value)
    )
    WikiPage.PagesList.Cards[0].CancelButton.click()


def test_page_changes_canceled(cancel_changes, wiki_page):
    WikiPage.PagesList.verify_pages([wiki_page])


@pytest.fixture(scope='module')
def edit_new_title(wiki_page, cancel_changes):
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        }),
        body=wiki.GetPageResponse.with_values(wiki_page.value)
    )
    WikiPage.PagesList.Cards[0].EditButton.click()
    time.sleep(0.5)

    title = fake.sentence()
    WikiPage.PagesList.Cards[0].TitleEdit.input(title)

    new_page = wiki.Page.with_values(wiki_page.value).with_values({
        wiki.Page.Title.name: title
    })
    wiki.UpdatePage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: new_page.Id.value
        }),
        body=wiki.UpdatePageResponse.with_values(new_page.value),
        reset=True
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: [new_page]
    }))
    WikiPage.PagesList.Cards[0].SaveButton.click()
    time.sleep(0.5)

    return title, new_page


def test_page_title_change_saved(edit_new_title):
    _, new_page = edit_new_title
    WikiPage.PagesList.verify_pages([new_page])


def test_update_page_request(edit_new_title, wiki_page):
    title, _ = edit_new_title
    wiki.UpdatePage.verify_called(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        }),
        expected=wiki.UpdatePageRequest.with_values({
            wiki.UpdatePageRequest.Title.name: title,
            wiki.UpdatePageRequest.Content.name: wiki_page.Content.value,
        })
    )


@pytest.fixture(scope='module')
def delete_page(wiki_page, edit_new_title):
    wiki.DeletePage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        })
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: []
    }))
    WikiPage.PagesList.Cards[0].DeleteButton.click()


def test_page_deleted(delete_page, wiki_page):
    WikiPage.PagesList.verify_pages([])


def test_delete_page(delete_page, wiki_page):
    wiki.DeletePage.verify_called(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: wiki_page.Id.value
        })
    )
