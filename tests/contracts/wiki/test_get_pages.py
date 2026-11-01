import pytest

from tests.contracts.utils.api import wiki as api
from tests.contracts.utils.calls.wiki import CreatePage, GetPages, Reset


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def simple_page(reset):
    result = CreatePage(
        title='First page',
    ).request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


@pytest.fixture(scope='module')
def full_page(simple_page):
    result = CreatePage(
        title='Second full page',
        content='Detailed content here',
    ).request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


def test_get_pages_empty():
    GetPages().request().verify()


def test_get_pages_single(simple_page):
    GetPages().request().verify(pages=[simple_page])


def test_get_pages_multiple(simple_page, full_page):
    GetPages().request().verify(pages=[simple_page, full_page])


def test_search_by_title(simple_page, full_page):
    GetPages(params=api.GetPagesParams.with_values({
        api.GetPagesParams.Query.name: 'First'
    })).request().verify(pages=[simple_page])


def test_search_by_content(simple_page, full_page):
    GetPages(params=api.GetPagesParams.with_values({
        api.GetPagesParams.Query.name: 'Detailed'
    })).request().verify(pages=[full_page])
