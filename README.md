# fastapi-exp

A small FastAPI experiment implementing an in-memory task management API.

## Requirements

- Python 3.11+
- fastapi
- uvicorn

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
```

## Run

```bash
uvicorn api.main:app --reload
```

The API will be available at http://127.0.0.1:8000, with interactive docs at http://127.0.0.1:8000/docs.

## Endpoints

- `GET /health` — health check
- `POST /tasks` — create a task
- `GET /tasks` — list tasks (supports `done` filter and `skip`/`limit` pagination)
- `GET /tasks/{task_id}` — get a task
- `PUT /tasks/{task_id}` — update a task
- `DELETE /tasks/{task_id}` — delete a task
