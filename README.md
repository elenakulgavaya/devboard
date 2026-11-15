# DevBoard

A micro team productivity hub — minimal task tracker + wiki. Built as a demo application for the [surety](https://surety.readthedocs.io/en/latest/) testing framework article series on [qaexplained.com](https://qaexplained.com).

## 🎤 As seen at CLC 2026

devboard is the demo app from the talk **"Your Pipeline Is Ready. Your Tests Are Not."** by Elena Kulgavaya (CLC 2026, Mannheim, 12 November 2026). The demo makes the same three changes twice: once with end-to-end tests after merge, and once with contract tests on every pull request.

- 📑 [Slides and talk summary](docs/talks/clc-2026/)
- ▶️ [The demo: end-to-end vs. contract tests](https://youtu.be/c41kOBuAqtA)
- ▶️ [The devboard app in one minute](https://youtu.be/7SOhgkAlFA0)

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
