import pytest

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks
from tests.contracts.utils.ui.pages.tasks import TasksPage


@pytest.fixture(scope='module', autouse=True)
def login():
    api_key = fake.password()
    LoginPage.open()
    LocalStorage.set_item(local_db.Keys.ApiKey, api_key)

    return api_key


@pytest.fixture(scope='module', autouse=True)
def load_task(login):
    task = tasks.Task()
    tasks.GetTasks.reply(times=2, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [task]
    }))
    tasks.GetTasksAssignees.reply()
    TasksPage.open()

    return task


@pytest.fixture(scope='module')
def open_comments(load_task):
    tasks.GetTaskComments.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value,
        }),
        body=tasks.GetTaskCommentsResponse.with_values({
            tasks.GetTaskCommentsResponse.Items.name: []
        })
    )
    TasksPage.TasksList.Cards[0].CommentsButton.click()


def test_comments(open_comments):
    TasksPage.TasksList.Cards[0].Comments.CommentsList.verify_labels([])



@pytest.fixture(scope='module')
def post_empty(open_comments):
    TasksPage.TasksList.Cards[0].Comments.PostButton.click()


def test_comment_errors(post_empty):
    TasksPage.TasksList.Cards[0].Comments.Errors.verify_labels([
        'Name is required', 'Comment is required'
    ])


@pytest.fixture(scope='module')
def add_author(post_empty):
    author = fake.name()
    TasksPage.TasksList.Cards[0].Comments.AuthorInput.input(author)

    return author


def test_author_value(add_author):
    TasksPage.TasksList.Cards[0].Comments.AuthorInput.verify_value(add_author)


@pytest.fixture(scope='module')
def add_content(add_author):
    content = fake.sentence()
    TasksPage.TasksList.Cards[0].Comments.CommentInput.input(content)

    return content


def test_content_value(add_content):
    TasksPage.TasksList.Cards[0].Comments.CommentInput.verify_value(
        add_content
    )


@pytest.fixture(scope='module')
def post_comment(load_task, add_author, add_content):
    comment = tasks.Comment.with_values({
        tasks.Comment.Author.name: add_author,
        tasks.Comment.Content.name: add_content,
    })
    tasks.CreateTaskComment.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value,
        }),
        body=tasks.CreateTaskCommentResponse.with_values(comment.value)
    )
    tasks.GetTaskComments.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value,
        }),
        body=tasks.GetTaskCommentsResponse.with_values({
            tasks.GetTaskCommentsResponse.Items.name: [comment]
        })
    )
    TasksPage.TasksList.Cards[0].Comments.PostButton.click()

    return comment


def test_comment_added(post_comment):
    TasksPage.TasksList.Cards[0].Comments.CommentsList.verify_labels([
        f'{post_comment.Author.value}\n{post_comment.Content.value}'
    ])


def test_comment_posted(post_comment, add_author, add_content, load_task):
    tasks.CreateTaskComment.verify_called(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value,
        }),
        expected=tasks.CreateTaskCommentRequest.with_values({
            tasks.CreateTaskCommentRequest.Author.name: add_author,
            tasks.CreateTaskCommentRequest.Content.name: add_content,
        })
    )
