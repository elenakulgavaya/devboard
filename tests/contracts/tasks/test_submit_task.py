import pytest
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import wiki
from tests.contracts.utils.calls.tasks import Reset, SubmitTask


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


def test_submit_task():
    SubmitTask().request().verify()


def test_submit_task_full():
    page_id = int(fake.random_number())
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
    )
    SubmitTask(is_full=True, page_id=page_id).request().verify()


def test_submit_task_get_pages_request():
    page_id = int(fake.random_number())
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
    )
    SubmitTask(is_full=True, page_id=page_id).request()
    wiki.GetPage.verify_called(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        })
    )


def test_submit_task_page_not_found():
    page_id = int(fake.random_number())
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
        status=404
    )
    SubmitTask(is_full=True, page_id=page_id).request().verify(error_code=422)


def test_submit_task_failed_to_get_page_ignored():
    page_id = int(fake.random_number())
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
        status=500
    )
    SubmitTask(is_full=True, page_id=page_id).request().verify()
