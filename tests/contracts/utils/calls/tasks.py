from datetime import datetime, timezone
from http.client import responses

from surety.api.caller import ApiCaller
from surety.diff import is_valid_uuid, precise_dates_equal_with_delta, \
    has_some_value, formatted_dates_equal_with_delta, get_fmt_date_with_delta
from surety.sdk.dates import Pattern
from surety.sdk.fakeable import fake

from tests.contracts.utils.api import tasks as api, auth

dates_equal_with_delta = get_fmt_date_with_delta(api.DATE_FORMAT)


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
                 status=None, due_date=None, priority=None, page_id=None):
        self.req_body = api.SubmitTaskRequest(is_full=is_full).with_values({
            api.SubmitTaskRequest.Title.name: title,
            api.SubmitTaskRequest.Description.name: description,
            api.SubmitTaskRequest.Status.name: status,
            api.SubmitTaskRequest.Priority.name: priority,
            api.SubmitTaskRequest.DueAt.name: due_date,
            api.SubmitTaskRequest.WikiPageId.name: page_id,
        })
        super().__init__(
            req_body=self.req_body,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: 'Wiki page not found'
            })
            rules = None
        else:
            error_code = 201
            resp_body = api.SubmitTaskResponse.with_values({
                api.SubmitTaskResponse.Title.name: self.req_body.Title.value,
                api.SubmitTaskResponse.Status.name: self.req_body.Status.value,
                api.SubmitTaskResponse.Priority.name:
                    self.req_body.Priority.value,
                api.SubmitTaskRequest.Labels.name: self.req_body.Labels.value,
                api.SubmitTaskRequest.WikiPageId.name:
                    self.req_body.WikiPageId.value,
                api.SubmitTaskRequest.Assignee.name:
                    self.req_body.Assignee.value,
                api.SubmitTaskRequest.Description.name:
                    self.req_body.Description.value,
                api.SubmitTaskResponse.DueAt.name: self.req_body.DueAt.value,
                api.SubmitTaskResponse.CreatedAt.name: datetime.now(timezone.utc),
                api.SubmitTaskResponse.UpdatedAt.name: datetime.now(timezone.utc),
            })
            rules = {
                api.SubmitTaskResponse.Id.name: has_some_value,
                api.SubmitTaskResponse.CreatedAt.name: dates_equal_with_delta,
                api.SubmitTaskResponse.UpdatedAt.name: dates_equal_with_delta,
            }

        super().verify_response(
            error_code=error_code,
            resp_body=resp_body,
            rules=rules
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


class GetTask(ApiCaller):
    contract = api.GetTask

    def __init__(self, task_id=None):
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, task=None, error_code=None):
        super().verify_response(
            error_code=error_code,
            resp_body=task and api.GetTaskResponse.with_values(task.value)
        )


class UpdateTask(ApiCaller):
    contract = api.UpdateTask

    def __init__(self, task_id=None, body=None):
        self.req_body = body or api.UpdateTaskRequest()
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            req_body=self.req_body,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, task=None, error_code=None, error_message='Task not found'):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: error_message
            })
            rules = None
        else:
            resp_body = task and api.GetTaskResponse.with_values(task.value).with_values(
                self.req_body.value and {
                    api.GetTaskResponse.UpdatedAt.name: datetime.now(timezone.utc),
                }
            ).with_values(self.req_body.value)
            rules = self.req_body.value and {
                api.GetTaskResponse.UpdatedAt.name: dates_equal_with_delta
            }

        super().verify_response(
            error_code=error_code,
            resp_body=resp_body,
            rules=rules
        )


class DeleteTask(ApiCaller):
    contract = api.DeleteTask

    def __init__(self, task_id=None):
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None):
        super().verify_response(error_code=error_code or 204)


class CreateTaskComment(ApiCaller):
    contract = api.CreateTaskComment

    def __init__(self, task_id=None):
        self.task_id = task_id
        self.req_body = api.CreateTaskCommentRequest()
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            req_body=self.req_body,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None):
        super().verify_response(
            error_code=error_code or 201,
            resp_body=api.CreateTaskCommentResponse.with_values({
                api.CreateTaskCommentResponse.TaskId.name: self.task_id,
                api.CreateTaskCommentResponse.CreatedAt.name:
                    datetime.now(timezone.utc),
            }).with_values(self.req_body.value) if error_code is None else None,
            rules={
                api.CreateTaskCommentResponse.Id.name: has_some_value,
                api.CreateTaskCommentResponse.CreatedAt.name:
                    dates_equal_with_delta,
            } if error_code is None else {}
        )


class GetTaskComments(ApiCaller):
    contract = api.GetTaskComments

    def __init__(self, task_id=None):
        self.task_id = task_id
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None, comments=None):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: 'Task not found',
            })
        else:
            resp_body = api.GetTaskCommentsResponse.with_values({
                api.GetTaskCommentsResponse.Items.name: comments or [],
                api.GetTaskCommentsResponse.Total.name: len(comments or []),
            })

        super().verify_response(
            error_code=error_code,
            resp_body=resp_body
        )


class GetTaskHistory(ApiCaller):
    contract = api.GetTaskHistory

    def __init__(self, task_id=None):
        self.task_id = task_id
        super().__init__(
            path_params=api.TaskPathParams.with_values({
                api.TaskPathParams.Id.name: task_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None, history=None):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: 'Task not found',
            })
            rules = {}
        else:
            resp_body = api.GetTaskHistoryResponse.with_values({
                api.GetTaskHistoryResponse.Items.name: history or [],
                api.GetTaskHistoryResponse.Total.name: len(history or []),
            })
            rules = {
                api.GetTaskHistoryResponse.Items.name: [{
                    api.HistoryEntry.Id.name: has_some_value,
                    api.HistoryEntry.ChangedAt.name: dates_equal_with_delta,
                }]
            }

        super().verify_response(
            error_code=error_code,
            resp_body=resp_body,
            rules=rules,
        )


class GetTasksAssignees(ApiCaller):
    contract = api.GetTasksAssignees

    def __init__(self):
        super().__init__(headers={'X-API-Key': 'devboard-dev-key'})

    def verify(self, assignees=None):
        super().verify_response(
            resp_body=api.GetTasksAssigneesResponse.with_values({
                api.GetTasksAssigneesResponse.Assignees.name: assignees or [],
            })
        )
