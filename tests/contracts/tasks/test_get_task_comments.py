import pytest

from tests.contracts.utils.api import tasks as api
from tests.contracts.utils.calls.tasks import (
    CreateTaskComment, GetTaskComments, Reset, SubmitTask
)


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def task_no_comments(reset):
    result = SubmitTask().request().verify_response(error_code=201)

    return api.Task().with_values(result.response.json())


@pytest.fixture(scope='module')
def task_one_comment(reset):
    result = SubmitTask().request().verify_response(error_code=201)
    task = api.Task().with_values(result.response.json())
    comment_result = CreateTaskComment(
        task_id=task.Id.value
    ).request().verify_response(error_code=201)

    return task, [api.Comment().with_values(comment_result.response.json())]


@pytest.fixture(scope='module')
def task_multiple_comments(reset):
    result = SubmitTask().request().verify_response(error_code=201)
    task = api.Task().with_values(result.response.json())
    comments = []

    for _ in range(3):
        _result = CreateTaskComment(
            task_id=task.Id.value
        ).request().verify_response(error_code=201)
        comments.append(api.Comment().with_values(_result.response.json()))

    return task, comments


def test_get_comments_no_task():
    GetTaskComments().request().verify(error_code=404)


def test_get_comments_no_comments(task_no_comments):
    GetTaskComments(task_id=task_no_comments.Id.value).request().verify()


def test_get_comments_single_comment(task_one_comment):
    task, comments = task_one_comment
    GetTaskComments(task_id=task.Id.value).request().verify(comments=comments)


def test_get_comments_multiple_comment(task_multiple_comments):
    task, comments = task_multiple_comments
    GetTaskComments(task_id=task.Id.value).request().verify(comments=comments)

