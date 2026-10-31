import pytest

from tests.contracts.utils.calls.tasks import Reset, SubmitTask


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


def test_submit_task():
    SubmitTask().request().verify()


def test_submit_task_full():
    SubmitTask(is_full=True).request().verify()

