from surety import Array, DateTime, Dictionary, Int, String, Raw
from surety.api import ApiContract, HttpMethod
from surety.config import Cfg

from tests.contracts.utils.api import tasks

SERVICE = 'wiki'
BASE_URL = Cfg.App.wiki_url

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class Page(Dictionary):
    Id = Int(name='id')
    Title = String(name='title')
    Content = String(name='content', allow_none=True)
    CreatedAt = DateTime(name='created_at', date_format=DATE_FORMAT)
    UpdatedAt = DateTime(name='updated_at', date_format=DATE_FORMAT)


class GetPagesParams(Dictionary):
    PageSize = Int(name='page_size', default=100)
    Query = String(name='q', required=False)


class GetPagesResponse(Dictionary):
    Items = Array(Page, name='items')
    Total = Int(name='total')
    Page = Int(name='page')
    PageSize = Int(name='page_size')


class CreateNewPageRequest(Dictionary):
    Title = String(name='title')
    Content = String(name='content', allow_none=True)


class CreateNewPageResponse(Page):
    pass


class PagePathParams(Dictionary):
    Id = Int(name='page_id')


class GetPageResponse(Page):
    pass


class UpdatePageRequest(Dictionary):
    Title = String(name='title',required=False)
    Content = String(name='content', required=False)


class UpdatePageResponse(Page):
    pass


class GetPageTasksResponse(Dictionary):
    PageId = Int(name='page_id')
    Tasks = Array(tasks.Task, name='items')


class ErrorResponse(Dictionary):
    Details = String(name='detail')


class GetPages(ApiContract):
    method = HttpMethod.GET
    url = '/pages'
    params = GetPagesParams
    resp_body = GetPagesResponse


class CreateNewPage(ApiContract):
    method = HttpMethod.POST
    url = '/pages'
    req_body = CreateNewPageRequest
    resp_body = CreateNewPageResponse


class GetPage(ApiContract):
    method = HttpMethod.GET
    url = '/pages/{page_id}'
    path_params = PagePathParams
    resp_body = GetPageResponse


class UpdatePage(ApiContract):
    method = HttpMethod.PATCH
    url = '/pages/{page_id}'
    path_params = PagePathParams
    req_body = UpdatePageRequest
    resp_body = UpdatePageResponse


class DeletePage(ApiContract):
    method = HttpMethod.DELETE
    url = '/pages/{page_id}'
    path_params = PagePathParams


class GetPageTasks(ApiContract):
    method = HttpMethod.GET
    url = '/pages/{page_id}/tasks'
    path_params = PagePathParams
    resp_body = GetPageTasksResponse


class Reset(ApiContract):
    method = HttpMethod.POST
    url = '/reset'
