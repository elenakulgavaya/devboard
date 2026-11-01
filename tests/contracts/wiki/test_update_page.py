import pytest

from tests.contracts.utils.api import wiki as api
from tests.contracts.utils.calls.wiki import CreatePage, UpdatePage, Reset


@pytest.fixture(scope='function', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='function')
def full_page(reset):
    result = CreatePage(
        title='Original Title',
        content='Original content',
    ).request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


@pytest.fixture(scope='function')
def page_no_content(reset):
    result = CreatePage(
        title='No Content'
    ).request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


def test_update_no_page():
    UpdatePage().request().verify(error_code=404)


def test_update_no_changes(full_page):
    UpdatePage(page_id=full_page.Id.value).request().verify(page=full_page)


def test_update_title(full_page):
    UpdatePage(
        page_id=full_page.Id.value,
        body=api.UpdatePageRequest.with_values({
            api.UpdatePageRequest.Title.name: 'Updated Title',
        })
    ).request().verify(page=full_page)


def test_update_content(full_page):
    UpdatePage(
        page_id=full_page.Id.value,
        body=api.UpdatePageRequest.with_values({
            api.UpdatePageRequest.Content.name: 'Updated content',
        })
    ).request().verify(page=full_page)


def test_update_both_fields(page_no_content):
    UpdatePage(
        page_id=page_no_content.Id.value,
        body=api.UpdatePageRequest.with_values({
            api.UpdatePageRequest.Title.name: 'New Title',
            api.UpdatePageRequest.Content.name: 'New content',
        })
    ).request().verify(page=page_no_content)
