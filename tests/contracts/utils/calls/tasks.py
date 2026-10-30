from datetime import datetime, timezone

from surety.api.caller import ApiCaller
from surety.diff import is_valid_uuid, precise_dates_equal_with_delta
from surety.sdk.dates import Pattern
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import tasks as api



class Reset(ApiCaller):
    contract = api.Reset

    def __init__(self, params=None):
        super().__init__(
            params=params,
            headers={'X-API-Key': 'devboard-dev-key'}
        )


class SubmitTask(ApiCaller):
    contract = api.SubmitTask

    def __init__(self, is_full=False, title=None, description=None,
                 status=None, due_date=None):
        super().__init__(
            req_body=api.SubmitTaskRequest(is_full=is_full).with_values({
                api.SubmitTaskRequest.Title.name: title,
                api.SubmitTaskRequest.Description.name: description,
                api.SubmitTaskRequest.Status.name: status,
                api.SubmitTaskRequest.DueAt.name: due_date,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )


class GetTasks(ApiCaller):
    contract = api.GetTasks

    def __init__(self, params=None):
        super().__init__(
            params=params,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, tasks=None):
        super().verify_response(resp_body=api.GetTasksResponse.with_values({
            api.GetTasksResponse.Items.name: tasks or [],
            api.GetTasksResponse.Total.name: len(tasks or []),
            api.GetTasksResponse.Page.name: 1,
            api.GetTasksResponse.PageSize.name: 100,
        }), normalize=True)

