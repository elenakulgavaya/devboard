import pytest

from datetime import datetime

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import tasks
from tests.contracts.utils.ui.pages.tasks import TasksPage


def history_entry_to_ui(history_entry):
    default = '—'
    date_format = '%b %-d, %I:%M %p'
    new_tz = str(datetime.now().astimezone().tzinfo)
    return (
        f'{history_entry.Field.value}\n'
        f'{history_entry.OldValue.value or default}\n→\n'
        f'{history_entry.NewValue.value or default}\n'
        f'{history_entry.ChangedAt.to_format(date_format, new_tz=new_tz)}\n'
    )


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
def open_history(load_task):
    history = [
        tasks.HistoryEntry.with_values({
            tasks.HistoryEntry.Field.name: 'status',
            tasks.HistoryEntry.OldValue.name: tasks.Status.Todo,
            tasks.HistoryEntry.NewValue.name: tasks.Status.InProgress,
        }),
        tasks.HistoryEntry.with_values({
            tasks.HistoryEntry.Field.name: 'assignee',
            tasks.HistoryEntry.NewValue.name: fake.name(),
        }),
        tasks.HistoryEntry.with_values({
            tasks.HistoryEntry.Field.name: 'priority',
            tasks.HistoryEntry.OldValue.name: tasks.Priority.High,
            tasks.HistoryEntry.NewValue.name: tasks.Priority.Medium,
        })
    ]
    tasks.GetTaskHistory.reply(
        path_params=tasks.TaskPathParams.with_values({
            tasks.TaskPathParams.Id.name: load_task.Id.value,
        }),
        body=tasks.GetTaskHistoryResponse.with_values({
            tasks.GetTaskHistoryResponse.Items.name: history
        })
    )
    TasksPage.TasksList.Cards[0].HistoryButton.click()

    return history

def test_history(open_history):
    TasksPage.TasksList.Cards[0].HistoryItems.verify_labels([
        history_entry_to_ui(entry) for entry in open_history
    ])
