from typing import Annotated
from fastapi import FastAPI, status, Depends, HTTPException, Header  # type: ignore[import]
from pydantic import BaseModel # type: ignore[import]
from dotenv import load_dotenv # type: ignore[import]

import os

class TaskIn(BaseModel):
    title: str
    description: str | None = None
    done: bool = False
    internal_note: str | None = None

class TaskOut(BaseModel):
    task_id: int
    title: str
    description: str | None = None
    done: bool = False

task_id = 0
tasks = {}

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("API_KEY")  # Get the API key from environment variables

async def get_existing_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

async def get_paginated_tasks(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    
    return x_api_key

app = FastAPI(dependencies=[Depends(verify_api_key)])

@app.get("/health")
async def health_check():
    return {"Message": "OK"}

@app.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn, _: Annotated[str, Depends(verify_api_key)]):
    global task_id
    task_id += 1
    tasks[task_id] = task
    return TaskOut(task_id=task_id, **task.dict())

@app.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task(task_id: int, task: Annotated[TaskIn, Depends(get_existing_task)]):
    return TaskOut(task_id=task_id, **task.dict())
    

@app.get("/tasks")
async def read_tasks(done: bool | None = None, pagination: Annotated[dict, Depends(get_paginated_tasks)] = None):
    filtered = [(tid, t) for tid, t in tasks.items() if done is None or t.done == done]
    skip, limit = pagination["skip"], pagination["limit"]
    page = filtered[skip : skip + limit]
    return [TaskOut(task_id=tid, **t.dict()) for tid, t in page]

@app.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskIn, existingtask: Annotated[TaskIn, Depends(get_existing_task)], _: Annotated[str, Depends(verify_api_key)]):
    
    tasks[task_id] = task
    return TaskOut(task_id=task_id, **task.dict())


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, task: Annotated[TaskIn, Depends(get_existing_task)]):
    tasks.pop(task_id)
    return None
