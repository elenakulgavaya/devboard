import pytest
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import tasks as api, wiki
from tests.contracts.utils.calls.tasks import GetTask, Reset, SubmitTask


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task(reset):
    result = SubmitTask().request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())

@pytest.fixture(scope='module')
def full_task(task):
    page_id = fake.random_number()
    wiki.GetPage.reply(
        path_params=wiki.PagePathParams.with_values({
            wiki.PagePathParams.Id.name: page_id
        }),
    )
    result = SubmitTask(
        is_full=True, page_id=page_id
    ).request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


def test_get_no_task():
    GetTask().request().verify(error_code=404)


def test_get_task(task):
    GetTask(task_id=task.Id.value).request().verify(task=task)


def test_get_full_task(full_task):
    GetTask(task_id=full_task.Id.value).request().verify(task=full_task)
