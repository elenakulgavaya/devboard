import random

from datetime import datetime, timedelta

from surety.diff import compare
from surety.ui import Button, Container, Label, Page, TextInput, Select
from surety.ui.browser import Elements

from tests.contracts.utils.api import tasks
from tests.contracts.utils.ui.pages.base import BasePage


def task_to_ui_dict(task):
    text_labels = [task.Title.value]
    badges = [task.Priority.value, f'👤 {task.Assignee.value}']

    if task.Description.value:
        text_labels.append(task.Description.value.replace('\n', ' '))

    if task.Labels.value:
        badges.extend(task.Labels.value.split(', '))

    if task.DueAt.value:
        badges.append(task.DueAt.to_format('Due %b %-d, %Y'))

    return {
        'labels': text_labels,
        'status': task.Status.value.replace('_', ' ').title(),
        'badges': badges
    }


class NewTaskForm(Container):
    Title = TextInput(css='#task-title')
    TitleError = Label(css='#task-title-err')
    Description = TextInput(css='#task-desc')
    Labels = TextInput(css='#task-labels')
    Status = Select(css='#task-status')
    Priority = Select(css='#task-priority')
    Assignee = TextInput(css='#task-assignee')
    DueAt = TextInput(css='#task-due-at')
    WikiPage = Select(css='#task-wiki-page')
    AssigneeList = Select(css='#assignees-list')

    SaveButton = Button(css='button[onclick^=submitTask]')
    CancelButton = Button(css='button[onclick^=closeTaskForm]')


class Comments(Container):
    CommentsList = Elements(css='div[id^=comments-list]>div')

    AuthorInput = TextInput(css='input[id*=comment-author]')
    CommentInput = TextInput(css='textarea[id*=comment-content]')
    PostButton = Button(css='button[onclick^=submitComment]')
    Errors = Elements(css='p[id$=-err]')


class TaskCard(Container):
    Labels = Elements(css='p', element_class=Label)
    StatusButton = Button(css='button[onclick^=cycleStatus]')
    Badges = Elements(css='span.rounded-full', element_class=Label)
    CommentsButton = Button(css='button[onclick*=comments]')
    HistoryButton = Button(css='button[onclick*=history]')
    EditButton = Button(css='button[onclick*=startEditTask]')
    DeleteButton = Button(css='button[onclick*=deleteTask]')

    Comments = Comments(css='div[id^=task-comments]')
    HistoryItems = Elements(css='div[id^=history-list]>div', element_class=Label)

    EditHeader = Label(css='p.font-semibold')
    TitleEdit = TextInput(css='input[id*=et-title]')
    DescriptionEdit = TextInput(css='textarea[id*=et-desc]')
    LabelsEdit = TextInput(css='input[id*=et-labels]')
    StatusEdit = Select(css='select[id*=et-status]')
    PriorityEdit = Select(css='select[id*=et-priority]')
    AssigneeEdit = TextInput(css='input[id*=et-assignee]')
    DueAtEdit = TextInput(css='input[id*=et-due]')
    WikiEdit = Select(css='input[id*=et-wiki]')

    SaveButton = Button(css='button[onclick^=saveEditTask]')
    CancelButton = Button(css='button[onclick^=cancelEditTask]')


    def to_dict(self):
        return {
            'labels': self.Labels.get_labels(),
            'status': self.StatusButton.text,
            'badges': self.Badges.get_labels(),
        }


class TasksList(Container):
    Cards = Elements(css='div.card', element_class=TaskCard)

    @property
    def tasks(self):
        return [task.to_dict() for task in self.Cards]

    def verify_tasks(self, tasks):
        self.Cards.wait_for_items_load(len(tasks))
        compare(
            actual=self.tasks,
            expected=[task_to_ui_dict(task) for task in tasks],
            target_name='tasks list'
        )


class TasksPage(BasePage):
    NewTaskButton = Button(css='button[onclick^=openTaskForm]')
    SearchInput = TextInput(css='#search-tasks')

    NewTask = NewTaskForm(css='#task-form')
    TasksList = TasksList(css='#tasks-list')

    AllTasks = Button(css='#filter-all')
    TodoTasks = Button(css='#filter-todo')
    InProgressTasks = Button(css='#filter-in_progress')
    DoneTasks = Button(css='#filter-done')
    OverdueTasks = Button(css='#filter-overdue')
