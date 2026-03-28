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

app = FastAPI(title="DevBoard Wiki Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "devboard-dev-key")
TASKS_SERVICE_URL = os.getenv("TASKS_SERVICE_URL", "http://localhost:8001")


# ── Auth ──────────────────────────────────────────────────

async def verify_api_key(x_api_key: str = Header(alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Health (no auth) ──────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "wiki"}


# ── Protected router ──────────────────────────────────────

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/pages", response_model=schemas.PageListResponse)
def list_pages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Page)
    if q:
        query = query.filter(
            or_(
                models.Page.title.ilike(f"%{q}%"),
                models.Page.content.ilike(f"%{q}%"),
            )
        )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return schemas.PageListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/pages", response_model=schemas.PageRead, status_code=201)
def create_page(payload: schemas.PageCreate, db: Session = Depends(get_db)):
    page = models.Page(**payload.model_dump())
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.get("/pages/{page_id}", response_model=schemas.PageRead)
def get_page(page_id: int, db: Session = Depends(get_db)):
    page = db.get(models.Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.patch("/pages/{page_id}", response_model=schemas.PageRead)
def update_page(page_id: int, payload: schemas.PageUpdate, db: Session = Depends(get_db)):
    page = db.get(models.Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(page, field, value)
    db.commit()
    db.refresh(page)
    return page


@router.delete("/pages/{page_id}", status_code=204)
def delete_page(page_id: int, db: Session = Depends(get_db)):
    page = db.get(models.Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete(page)
    db.commit()


@router.get("/pages/{page_id}/tasks", response_model=schemas.LinkedTasksResponse)
def get_linked_tasks(page_id: int, db: Session = Depends(get_db)):
    """Cross-service call: fetch tasks linked to this wiki page from the Tasks service."""
    if not db.get(models.Page, page_id):
        raise HTTPException(status_code=404, detail="Page not found")

    with httpx.Client() as client:
        response = client.get(
            f"{TASKS_SERVICE_URL}/tasks",
            params={"wiki_page_id": page_id, "page_size": 100},
            headers={"X-API-Key": API_KEY},
        )
        response.raise_for_status()

    return schemas.LinkedTasksResponse(page_id=page_id, tasks=response.json().get("items", []))


# ── Internal endpoints (service-to-service) ───────────────

@router.post("/internal/reindex", status_code=204)
def reindex_task(payload: schemas.TaskIndexUpdate, db: Session = Depends(get_db)):
    """Called by the Tasks service when a task description changes."""
    existing = db.get(models.TaskIndex, payload.task_id)
    if existing:
        existing.description = payload.description
        existing.indexed_at = datetime.now(timezone.utc)
    else:
        db.add(models.TaskIndex(**payload.model_dump()))
    db.commit()


@router.get("/internal/task-index", response_model=list[schemas.TaskIndexRead])
def list_task_index(db: Session = Depends(get_db)):
    """View all task descriptions indexed by this service — useful for testing side effects."""
    return db.query(models.TaskIndex).order_by(models.TaskIndex.indexed_at.desc()).all()


app.include_router(router)
