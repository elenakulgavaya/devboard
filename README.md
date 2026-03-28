# DevBoard

A micro team productivity hub — minimal task tracker + wiki. Built as a demo application for the [surety](https://surety.readthedocs.io/en/latest/) testing framework article series on [qaexplained.com](https://qaexplained.com).

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Tasks Service  │◄─────────────►│  Wiki Service   │
│  FastAPI :8001  │               │  FastAPI :8002  │
│  SQLite         │               │  SQLite         │
└─────────────────┘               └─────────────────┘
         ▲                                 ▲
         └──────────────┬──────────────────┘
                        │ fetch()
               ┌────────┴────────┐
               │    Frontend     │
               │ Vanilla JS :3000│
               │ localStorage    │
               └─────────────────┘
```

## Quick Start

```bash
docker compose up --build
```

- Frontend: http://localhost:3010
- Tasks API: http://localhost:8001/docs
- Wiki API: http://localhost:8002/docs

## Project Structure

```
devboard/
├── services/
│   ├── tasks/          # FastAPI tasks microservice (port 8001)
│   └── wiki/           # FastAPI wiki microservice (port 8002)
├── frontend/           # Vanilla JS SPA
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Services

### Tasks Service (`/tasks`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List tasks (pagination, filter by status/priority/assignee) |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get task |
| PATCH | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

### Wiki Service (`/pages`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/pages` | List pages (pagination) |
| POST | `/pages` | Create page |
| GET | `/pages/{id}` | Get page |
| PATCH | `/pages/{id}` | Update page |
| DELETE | `/pages/{id}` | Delete page |
| GET | `/pages/{id}/tasks` | Get tasks linked to this page (cross-service call) |
