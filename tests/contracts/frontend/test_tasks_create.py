import pytest

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.local_db import Keys
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks, wiki
from tests.contracts.utils.ui.pages.tasks import TasksPage


@pytest.fixture(scope='module', autouse=True)
def login():
    api_key = fake.password()
    LoginPage.open()
    LocalStorage.set_item(local_db.Keys.ApiKey, api_key)

    return api_key

@pytest.fixture(scope='module', autouse=True)
def tasks_page(login):
    tasks.GetTasks.reply(times=2)
    tasks.GetTasksAssignees.reply()
    TasksPage.open()


def test_new_task_form_is_closed(tasks_page):
    assert TasksPage.NewTask.is_not_present()


@pytest.fixture(scope='module')
def click_new_task():
    wiki.GetPages.reply()
    TasksPage.NewTaskButton.click()


def test_new_task_button_opens_form(click_new_task):
    TasksPage.NewTask.wait_for_load()


@pytest.fixture(scope='module')
def click_cancel(click_new_task):
    TasksPage.NewTask.CancelButton.click()


def test_cancel_button_closes_task_form(click_cancel):
    TasksPage.NewTask.wait_for_not_present()


@pytest.fixture(scope='module')
def submit_empty(click_cancel):
    wiki.GetPages.reply()
    TasksPage.NewTaskButton.click()
    TasksPage.NewTask.SaveButton.click()


def test_create_task_requires_title(submit_empty):
    TasksPage.NewTask.TitleError.verify_text('Title is required')


def test_create_task_no_title_form_remains_open(submit_empty):
    assert TasksPage.NewTask.is_present()


@pytest.fixture(scope='module')
def enter_title(submit_empty):
    title = fake.sentence()
    TasksPage.NewTask.Title.input(title)
    return title


def test_title_value(enter_title):
    TasksPage.NewTask.Title.verify_value(enter_title)


def test_verify_title_in_draft(enter_title):
    LocalStorage.verify_item(
        key=Keys.TaskDraft,
        expected=local_db.TaskDraft.with_values({
            local_db.TaskDraft.Title.name: enter_title,
            local_db.TaskDraft.Description.name: '',
            local_db.TaskDraft.Labels.name: '',
        }).value
    )


@pytest.fixture(scope='module')
def assignees():
    return [fake.name() for _ in range(4)]


@pytest.fixture(scope='module')
def pages():
    return [wiki.Page() for i in range(4)]


@pytest.fixture(scope='module')
def submit_title(enter_title, assignees, pages):
    new_task = tasks.Task.with_values({
        tasks.Task.Title.name: enter_title,
    })
    tasks.SubmitTask.reply(
        body=tasks.SubmitTaskResponse.with_values(new_task.value),
        reset=True
    )
    tasks.GetTasks.reply(body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [new_task]
    }))
    tasks.GetTasksAssignees.reply(
        body=tasks.GetTasksAssigneesResponse.with_values({
            tasks.GetTasksAssigneesResponse.Assignees.name: assignees
        })
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: pages
    }))
    TasksPage.NewTask.SaveButton.click()

    return new_task


def test_new_task_form_closed(submit_title):
    assert TasksPage.NewTask.is_not_present()

def test_verify_draft_cleared(submit_title):
    LocalStorage.verify_item(key=Keys.TaskDraft, expected=None)

def test_submit_talk_request(submit_title, enter_title):
    tasks.SubmitTask.verify_called(
        expected=tasks.SubmitTaskRequest.with_values({
            tasks.SubmitTaskRequest.Title.name: enter_title,
            tasks.SubmitTaskRequest.Status.name: tasks.Status.Todo,
            tasks.SubmitTaskRequest.Priority.name: tasks.Priority.Medium,
        })
    )

def test_new_task_in_the_list(submit_title):
    TasksPage.TasksList.verify_tasks([submit_title])


@pytest.fixture(scope='module')
def add_another(submit_title):
    TasksPage.NewTaskButton.click()


def test_title_reset(add_another):
    TasksPage.NewTask.Title.verify_value('')


@pytest.fixture(scope='module')
def new_title(add_another):
    title = fake.sentence()
    TasksPage.NewTask.Title.input(title)

    return title


def test_new_title(new_title):
    TasksPage.NewTask.Title.verify_value(new_title)


@pytest.fixture(scope='module')
def description(new_title):
    description = fake.sentence()
    TasksPage.NewTask.Description.input(description)

    return description


def test_description(description):
    TasksPage.NewTask.Description.verify_value(description)


@pytest.fixture(scope='module')
def labels(new_title):
    labels = 'bug, urgent'
    TasksPage.NewTask.Labels.input(labels)

    return labels


def test_labels(labels):
    TasksPage.NewTask.Labels.verify_value(labels)


@pytest.fixture(scope='module')
def select_status(labels):
    TasksPage.NewTask.Status.select(value='in_progress')
    return tasks.Status.InProgress


def test_status_selected(select_status):
    TasksPage.NewTask.Status.verify_selected_option('In Progress')


@pytest.fixture(scope='module')
def select_priority(select_status):
    TasksPage.NewTask.Priority.select(value='high')
    return tasks.Priority.High


def test_priority_selected(select_priority):
    TasksPage.NewTask.Priority.verify_selected_option('High')


@pytest.fixture(scope='module')
def input_assignee(select_priority):
    assignee = fake.name()
    TasksPage.NewTask.Assignee.input(assignee)

    return assignee


def test_assignee(input_assignee):
    TasksPage.NewTask.Assignee.verify_value(input_assignee)


def test_verify_full_draft(new_title, description, labels, input_assignee):
    LocalStorage.verify_item(
        key=Keys.TaskDraft,
        expected=local_db.TaskDraft.with_values({
            local_db.TaskDraft.Title.name: new_title,
            local_db.TaskDraft.Description.name: description,
            local_db.TaskDraft.Labels.name: labels,
        }).value
    )

@pytest.fixture(scope='module')
def submit_full(submit_title, assignees, pages, input_assignee,
                new_title, select_priority, select_status, labels,
                description):
    full_task = tasks.Task.with_values({
        tasks.Task.Title.name: new_title,
        tasks.Task.Description.name: description,
        tasks.Task.Labels.name: labels,
        tasks.Task.Assignee.name: input_assignee,
        tasks.Task.Priority.name: select_priority,
        tasks.Task.Status.name: select_status,
    })
    tasks.SubmitTask.reply(
        body=tasks.SubmitTaskResponse.with_values(full_task.value),
        reset=True
    )
    tasks.GetTasks.reply(body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [submit_title, full_task]
    }))
    tasks.GetTasksAssignees.reply(
        body=tasks.GetTasksAssigneesResponse.with_values({
            tasks.GetTasksAssigneesResponse.Assignees.name: assignees
        })
    )
    wiki.GetPages.reply(body=wiki.GetPagesResponse.with_values({
        wiki.GetPagesResponse.Items.name: pages
    }))
    TasksPage.NewTask.SaveButton.click()

    return full_task


def test_submit_full_talk_request(submit_full, input_assignee, new_title,
                                  select_priority, select_status, labels,
                                  description):
    tasks.SubmitTask.verify_called(
        expected=tasks.SubmitTaskRequest.with_values({
            tasks.SubmitTaskRequest.Title.name: new_title,
            tasks.SubmitTaskRequest.Description.name: description,
            tasks.SubmitTaskRequest.Labels.name: labels,
            tasks.SubmitTaskRequest.Status.name: select_status,
            tasks.SubmitTaskRequest.Priority.name: select_priority,
            tasks.SubmitTaskRequest.Assignee.name: input_assignee,
        }), timeout=2
    )


def test_new_full_task_in_the_list(submit_title, submit_full):
    TasksPage.TasksList.verify_tasks([submit_title, submit_full])


@pytest.fixture(scope='module')
def reopen_task_form(submit_full):
    TasksPage.NewTaskButton.click()


def test_title_is_cleared(reopen_task_form):
    TasksPage.NewTask.Title.verify_value('')


def test_description_is_cleared(reopen_task_form):
    TasksPage.NewTask.Description.verify_value('')
