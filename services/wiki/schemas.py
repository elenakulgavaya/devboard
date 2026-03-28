from datetime import datetime

from pydantic import BaseModel


class PageBase(BaseModel):
    title: str
    content: str | None = None


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PageRead(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PageListResponse(BaseModel):
    items: list[PageRead]
    total: int
    page: int
    page_size: int


class LinkedTasksResponse(BaseModel):
    page_id: int
    tasks: list[dict]


class TaskIndexUpdate(BaseModel):
    task_id: int
    description: str | None = None


class TaskIndexRead(BaseModel):
    task_id: int
    description: str | None
    indexed_at: datetime

    model_config = {"from_attributes": True}
