from surety import Array, Dictionary, Int, String
from surety.api import ApiContract, HttpMethod
from surety.config import Cfg


SERVICE = 'wiki/'
BASE_URL = Cfg.App.api_url


class Page(Dictionary):
    Id = Int(name='id')
    Title = String(name='title')
    Content = String(name='content')


class GetPagesResponse(Dictionary):
    Items = Array(Page, name='items')


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


class GetPages(ApiContract):
    method = HttpMethod.GET
    url = 'pages'
    resp_body = GetPagesResponse


class CreateNewPage(ApiContract):
    method = HttpMethod.POST
    url = 'pages'
    req_body = CreateNewPageRequest
    resp_body = CreateNewPageResponse


class GetPage(ApiContract):
    method = HttpMethod.GET
    url = 'pages/{page_id}'
    resp_body = GetPageResponse


class UpdatePage(ApiContract):
    method = HttpMethod.PATCH
    url = 'pages/{page_id}'
    req_body = UpdatePageRequest
    resp_body = UpdatePageResponse


class DeletePage(ApiContract):
    method = HttpMethod.DELETE
    url = 'pages/{page_id}'
