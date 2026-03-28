import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevBoard Tasks Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY        = os.getenv("API_KEY", "devboard-dev-key")
WIKI_SERVICE_URL = os.getenv("WIKI_SERVICE_URL", "http://localhost:8002")
ADMIN_USER     = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


# ── Auth ──────────────────────────────────────────────────

async def verify_api_key(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Health & login (no auth) ──────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "tasks"}


@app.post("/auth/login")
def login(payload: dict):
    if payload.get("username") == ADMIN_USER and payload.get("password") == ADMIN_PASSWORD:
        return {"api_key": API_KEY}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ── Protected router ──────────────────────────────────────

router = APIRouter(dependencies=[Depends(verify_api_key)])

TRACKED_FIELDS = [
    "title", "description", "status", "priority",
    "assignee", "labels", "wiki_page_id", "due_at",
]


@router.get("/tasks", response_model=schemas.TaskListResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    assignee: str | None = Query(None),
    wiki_page_id: int | None = Query(None),
    q: str | None = Query(None),
    overdue: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if assignee:
        query = query.filter(models.Task.assignee == assignee)
    if wiki_page_id is not None:
        query = query.filter(models.Task.wiki_page_id == wiki_page_id)
    if q:
        query = query.filter(
            or_(
                models.Task.title.ilike(f"%{q}%"),
                models.Task.description.ilike(f"%{q}%"),
            )
        )
    if overdue:
        now = datetime.utcnow()
        query = query.filter(
            models.Task.due_at.is_not(None),
            models.Task.due_at < now,
            models.Task.status != "done",
        )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return schemas.TaskListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/tasks", response_model=schemas.TaskRead, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    description_changed = False

    for field, new_value in update_data.items():
        old_value = getattr(task, field)
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None
        if old_str != new_str and field in TRACKED_FIELDS:
            db.add(models.TaskHistory(
                task_id=task_id,
                field=field,
                old_value=old_str,
                new_value=new_str,
            ))
        if field == "description" and old_str != new_str:
            description_changed = True
        setattr(task, field, new_value)

    db.commit()
    db.refresh(task)

    if description_changed:
        _notify_wiki_reindex(task_id, task.description)

    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.get("/tasks/{task_id}/comments", response_model=schemas.CommentListResponse)
def list_comments(task_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    items = (
        db.query(models.Comment)
        .filter(models.Comment.task_id == task_id)
        .order_by(models.Comment.created_at)
        .all()
    )
    return schemas.CommentListResponse(items=items, total=len(items))


@router.post("/tasks/{task_id}/comments", response_model=schemas.CommentRead, status_code=201)
def add_comment(task_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    comment = models.Comment(task_id=task_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/tasks/{task_id}/history", response_model=schemas.TaskHistoryListResponse)
def get_task_history(task_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    items = (
        db.query(models.TaskHistory)
        .filter(models.TaskHistory.task_id == task_id)
        .order_by(models.TaskHistory.changed_at.desc())
        .all()
    )
    return schemas.TaskHistoryListResponse(items=items, total=len(items))


@app.get("/tasks/assignees", response_model=schemas.AssigneesResponse, dependencies=[Depends(verify_api_key)])
def list_assignees(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Task.assignee)
        .filter(models.Task.assignee.is_not(None))
        .distinct()
        .all()
    )
    return schemas.AssigneesResponse(assignees=[r[0] for r in rows])


app.include_router(router)


# ── Helpers ───────────────────────────────────────────────

def _notify_wiki_reindex(task_id: int, description: str | None) -> None:
    """Fire-and-forget call to wiki service. Wiki being down must not fail task updates."""
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post(
                f"{WIKI_SERVICE_URL}/internal/reindex",
                json={"task_id": task_id, "description": description},
                headers={"X-API-Key": API_KEY},
            )
    except Exception:
        pass
