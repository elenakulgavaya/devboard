import pytest

from tests.contracts.utils.api import wiki as api
from tests.contracts.utils.calls.wiki import CreatePage, GetPage, Reset


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def simple_page(reset):
    result = CreatePage().request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


@pytest.fixture(scope='module')
def full_page(simple_page):
    result = CreatePage(is_full=True).request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


def test_get_no_page():
    GetPage().request().verify(error_code=404)


def test_get_page(simple_page):
    GetPage(page_id=simple_page.Id.value).request().verify(page=simple_page)


def test_get_full_page(full_page):
    GetPage(page_id=full_page.Id.value).request().verify(page=full_page)
