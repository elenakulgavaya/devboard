from surety import Array, DateTime, Enum, Dictionary, Int, String, Bool
from surety.api import ApiContract, HttpMethod
from surety.config import Cfg
from surety.sdk.fakeable import fake

SERVICE = 'api'
BASE_URL = Cfg.App.tasks_url


class Status(Enum):
    Todo = 'todo'
    InProgress = 'in_progress'
    Done = 'done'


class Priority(Enum):
    Low = 'low'
    Medium = 'medium'
    High = 'high'


class Task(Dictionary):
    Id = Int(name='id')
    Title = String(name='title')
    Description = String(name='description', allow_none=True)
    Labels = String(name='labels', allow_none=True)
    Status = Status(name='status')
    Priority = Priority(name='priority')
    Assignee = String(name='assignee', allow_none=True)
    DueAt = DateTime(name='due_at', allow_none=True)
    DueAt = DateTime(name='due_at', allow_none=True)
    WikiPageId = Int(name='wiki_page_id', allow_none=True)
    CreatedAt = DateTime(name='created_at')
    UpdatedAt = DateTime(name='updated_at')


class GetTasksResponse(Dictionary):
    Items = Array(Task, name='items')
    Total = Int(name='total')
    Page = Int(name='page')
    PageSize = Int(name='page_size')


class SubmitTaskRequest(Dictionary):
    Title = String(name='title')
    Description = String(name='description', allow_none=True)
    Labels = String(name='labels', allow_none=True)
    Status = Status(name='status')
    Priority = Priority(name='priority')
    Assignee = String(name='assignee', allow_none=True)
    DueAt = DateTime(name='due_at', allow_none=True)
    WikiPageId = Int(name='wiki_page_id', allow_none=True)


class SubmitTaskResponse(Task):
    pass


class TaskPathParams(Dictionary):
    Id = Int(name='task_id')


class GetTaskResponse(Task):
    pass


class UpdateTaskStatusRequest(Dictionary):
    Status = Status(name='status')


class UpdateTaskRequest(Dictionary):
    Title = String(name='title', required=False)
    Description = String(name='description', required=False)
    Labels = String(name='labels', required=False)
    Status = Status(name='status', required=False)
    Priority = Priority(name='priority', required=False)
    Assignee = String(name='assignee', required=False)
    DueAt = DateTime(name='due_at', required=False)
    WikiPageId = Int(name='wiki_page_id', allow_none=True)


class UpdateTaskResponse(Task):
    pass


class Comment(Dictionary):
    Author = String(name='author')
    Content = String(name='content')
    Created = DateTime(name='created')


class GetTaskCommentsResponse(Dictionary):
    Items = Array(Comment, name='items')


class CreateTaskCommentRequest(Dictionary):
    Author = String(name='author')
    Content = String(name='content')


class CreateTaskCommentResponse(Comment):
    pass


class HistoryEntry(Dictionary):
    Field = String(name='field')
    OldValue = String(name='old_value', required=False)
    NewValue = String(name='new_value', required=False)
    ChangedAt = DateTime(name='changed_at')


class GetTaskHistoryResponse(Dictionary):
    Items = Array(HistoryEntry, name='items')


class GetTasksAssigneesResponse(Dictionary):
    Assignees = Array(String(fake_as=fake.name), name='assignees')


class GetTasksParams(Dictionary):
    PageSize = Int(name='page_size', default=100)
    Query = String(name='q', required=False)
    Status = Status(name='status', required=False)
    Overdue = Bool(name='overdue', required=False)


class GetTasks(ApiContract):
    method = HttpMethod.GET
    url = '/tasks'
    params = GetTasksParams
    resp_body = GetTasksResponse


class SubmitTask(ApiContract):
    method = HttpMethod.POST
    url = '/tasks'
    req_body = SubmitTaskRequest
    resp_body = SubmitTaskResponse


class GetTask(ApiContract):
    method = HttpMethod.GET
    url = '/tasks/{task_id}'
    path_params = TaskPathParams
    resp_body = GetTaskResponse


class UpdateTask(ApiContract):
    method = HttpMethod.PATCH
    url = '/tasks/{task_id}'
    path_params = TaskPathParams
    req_body = UpdateTaskRequest
    resp_body = UpdateTaskResponse


class DeleteTask(ApiContract):
    method = HttpMethod.DELETE
    url = '/tasks/{task_id}'
    path_params = TaskPathParams


class GetTaskComments(ApiContract):
    method = HttpMethod.GET
    url = '/tasks/{task_id}/comments'
    path_params = TaskPathParams
    resp_body = GetTaskCommentsResponse


class CreateTaskComment(ApiContract):
    method = HttpMethod.POST
    url = '/tasks/{task_id}/comments'
    path_params = TaskPathParams
    req_body = CreateTaskCommentRequest
    resp_body = CreateTaskCommentResponse


class GetTaskHistory(ApiContract):
    method = HttpMethod.GET
    url = '/tasks/{task_id}/history'
    path_params = TaskPathParams
    resp_body = GetTaskHistoryResponse


class GetTasksAssignees(ApiContract):
    method = HttpMethod.GET
    url = '/tasks/assignees'
    resp_body = GetTasksAssigneesResponse

class Reset(ApiContract):
    method = HttpMethod.POST
    url = '/reset'
