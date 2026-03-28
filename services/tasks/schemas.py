from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, field_validator


def _to_naive_utc(v: datetime | None) -> datetime | None:
    """Strip timezone, converting to UTC first. Keeps SQLite comparisons consistent."""
    if v is not None and v.tzinfo is not None:
        return v.astimezone(timezone.utc).replace(tzinfo=None)
    return v

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee: str | None = None
    labels: str | None = None
    wiki_page_id: int | None = None
    due_at: datetime | None = None

    @field_validator("due_at", mode="after")
    @classmethod
    def normalize_due_at(cls, v: datetime | None) -> datetime | None:
        return _to_naive_utc(v)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee: str | None = None
    labels: str | None = None
    wiki_page_id: int | None = None
    due_at: datetime | None = None

    @field_validator("due_at", mode="after")
    @classmethod
    def normalize_due_at(cls, v: datetime | None) -> datetime | None:
        return _to_naive_utc(v)


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int


class AssigneesResponse(BaseModel):
    assignees: list[str]


class CommentCreate(BaseModel):
    author: str
    content: str


class CommentRead(BaseModel):
    id: int
    task_id: int
    author: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    items: list[CommentRead]
    total: int


class TaskHistoryRead(BaseModel):
    id: int
    task_id: int
    field: str
    old_value: str | None
    new_value: str | None
    changed_at: datetime

    model_config = {"from_attributes": True}


class TaskHistoryListResponse(BaseModel):
    items: list[TaskHistoryRead]
    total: int
