import pytest

from tests.contracts.utils.calls.wiki import CreatePage, Reset


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


def test_create_minimal_page():
    CreatePage().request().verify()



def test_create_full_page():
    CreatePage(is_full=True).request().verify()
