import pytest

from tests.contracts.utils.api import wiki as api, tasks
from tests.contracts.utils.calls.wiki import CreatePage, GetPageTasks, Reset


@pytest.fixture(scope='module', autouse=True)
def reset():
    Reset().request().verify_response()


@pytest.fixture(scope='module')
def wiki_page(reset):
    result = CreatePage().request().verify_response(error_code=201)

    return api.Page().with_values(result.response.json())


def test_get_tasks_no_page():
    GetPageTasks().request().verify(error_code=404)


def test_get_tasks_empty_page(wiki_page):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [],
    }))
    GetPageTasks(page_id=wiki_page.Id.value).request().verify(
        tasks=[]
    )


def test_get_tasks_with_tasks(wiki_page):
    task = tasks.Task.with_values({
        tasks.Task.WikiPageId.name: wiki_page.Id.value,
    })
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [task],
    }))
    GetPageTasks(page_id=wiki_page.Id.value).request().verify(
        tasks=[task.value]
    )


def test_get_tasks_calls_tasks_service_with_page_filter(wiki_page):
    tasks.GetTasks.reply(reset=True, body=tasks.GetTasksResponse.with_values({
        tasks.GetTasksResponse.Items.name: [],
    }))
    GetPageTasks(page_id=wiki_page.Id.value).request().verify_response()
    tasks.GetTasks.verify_called(
        params={
            tasks.GetTasksParams.WikiPageId.name: [str(wiki_page.Id.value)],
            tasks.GetTasksParams.PageSize.name: ['100'],
        }
    )
