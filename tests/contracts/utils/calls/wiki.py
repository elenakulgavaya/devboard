from datetime import datetime, timezone

from surety.api.caller import ApiCaller
from surety.diff import has_some_value, get_fmt_date_with_delta

from tests.contracts.utils.api import wiki as api

dates_equal_with_delta = get_fmt_date_with_delta(api.DATE_FORMAT)


class Reset(ApiCaller):
    contract = api.Reset

    def __init__(self):
        super().__init__(headers={'X-API-Key': 'devboard-dev-key'})


class CreatePage(ApiCaller):
    contract = api.CreateNewPage

    def __init__(self, is_full=False, title=None, content=None):
        self.req_body = api.CreateNewPageRequest(is_full=is_full).with_values({
            api.CreateNewPageRequest.Title.name: title,
            api.CreateNewPageRequest.Content.name: content,
        })
        super().__init__(
            req_body=self.req_body,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self):
        super().verify_response(
            error_code=201,
            resp_body=api.CreateNewPageResponse.with_values({
                api.CreateNewPageResponse.Title.name:
                    self.req_body.Title.value,
                api.CreateNewPageResponse.Content.name:
                    self.req_body.Content.value,
                api.CreateNewPageResponse.CreatedAt.name:
                    datetime.now(timezone.utc),
                api.CreateNewPageResponse.UpdatedAt.name:
                    datetime.now(timezone.utc),
            }),
            rules={
                api.CreateNewPageResponse.Id.name: has_some_value,
                api.CreateNewPageResponse.CreatedAt.name:
                    dates_equal_with_delta,
                api.CreateNewPageResponse.UpdatedAt.name:
                    dates_equal_with_delta,
            }
        )


class GetPages(ApiCaller):
    contract = api.GetPages

    def __init__(self, params=None):
        super().__init__(
            params=params,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, pages=None):
        super().verify_response(resp_body=api.GetPagesResponse.with_values({
            api.GetPagesResponse.Items.name: pages or [],
            api.GetPagesResponse.Total.name: len(pages or []),
            api.GetPagesResponse.Page.name: 1,
            api.GetPagesResponse.PageSize.name: 100,
        }), normalize=True)


class GetPage(ApiCaller):
    contract = api.GetPage

    def __init__(self, page_id=None):
        super().__init__(
            path_params=api.PagePathParams.with_values({
                api.PagePathParams.Id.name: page_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, page=None, error_code=None):
        super().verify_response(
            error_code=error_code,
            resp_body=page and api.GetPageResponse.with_values(page.value)
        )


class UpdatePage(ApiCaller):
    contract = api.UpdatePage

    def __init__(self, page_id=None, body=None):
        self.req_body = body or api.UpdatePageRequest()
        super().__init__(
            path_params=api.PagePathParams.with_values({
                api.PagePathParams.Id.name: page_id,
            }),
            req_body=self.req_body,
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, page=None, error_code=None):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: 'Page not found'
            })
            rules = None
        else:
            resp_body = page and api.UpdatePageResponse.with_values(page.value).with_values(
                self.req_body.value and {
                    api.UpdatePageResponse.UpdatedAt.name: datetime.now(timezone.utc),
                }
            ).with_values(self.req_body.value)
            rules = self.req_body.value and {
                api.UpdatePageResponse.UpdatedAt.name: dates_equal_with_delta
            }

        super().verify_response(
            error_code=error_code, resp_body=resp_body, rules=rules
        )


class DeletePage(ApiCaller):
    contract = api.DeletePage

    def __init__(self, page_id=None):
        super().__init__(
            path_params=api.PagePathParams.with_values({
                api.PagePathParams.Id.name: page_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, error_code=None):
        super().verify_response(error_code=error_code or 204)


class GetPageTasks(ApiCaller):
    contract = api.GetPageTasks

    def __init__(self, page_id=None):
        self.page_id = page_id
        super().__init__(
            path_params=api.PagePathParams.with_values({
                api.PagePathParams.Id.name: page_id,
            }),
            headers={'X-API-Key': 'devboard-dev-key'}
        )

    def verify(self, tasks=None, error_code=None):
        if error_code:
            resp_body = api.ErrorResponse.with_values({
                api.ErrorResponse.Details.name: 'Page not found'
            })
        else:
            resp_body = api.GetPageTasksResponse.with_values({
                api.GetPageTasksResponse.PageId.name: self.page_id,
                api.GetPageTasksResponse.Tasks.name: tasks or [],
            })

        super().verify_response(
            error_code=error_code,
            resp_body=resp_body,
            normalize=True
        )
