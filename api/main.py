from typing import Annotated
from fastapi import FastAPI, status, Depends, HTTPException, Header, APIRouter  # type: ignore[import]
from pydantic import BaseModel # type: ignore[import]
from dotenv import load_dotenv # type: ignore[import]

import os

# Pydantic models for request and response validation
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

# Global variables to store tasks in memory
task_id = 0
tasks = {}

# Load environment variables from .env file
load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variables
API_KEY = os.getenv("API_KEY")  # Get the API key from environment variables

# Dependency functions for task management and API key verification
async def get_existing_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

# Dependency function for pagination
async def get_paginated_tasks(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Dependency function to verify the API key in request headers
async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    
    return x_api_key

# Create FastAPI app instance
app = FastAPI()

# showcase of using dependencies with routers - public routes do not require an API key, while private routes do
# here private routes are protected by the verify_api_key dependency, which checks for a valid API key in the request headers
# health check route is public and does not require an API key, while task management routes are private and require a valid API key
public = APIRouter()
private = APIRouter(dependencies=[Depends(verify_api_key)])

app.include_router(public)
app.include_router(private)

# Public route for health check
@public.get("/health")
async def health_check():
    return {"Message": "OK"}

# Private routes for task management 
# HTTPPost for creating a new task, HTTPGet for reading a specific task or all tasks, 
# HTTPPut for updating a task, and HTTPDelete for deleting a task

@private.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn, _: Annotated[str, Depends(verify_api_key)]):
    global task_id
    task_id += 1
    tasks[task_id] = task
    return TaskOut(task_id=task_id, **task.dict())

@private.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task(task_id: int, task: Annotated[TaskIn, Depends(get_existing_task)]):
    return TaskOut(task_id=task_id, **task.dict())
    

@private.get("/tasks")
async def read_tasks(done: bool | None = None, pagination: Annotated[dict, Depends(get_paginated_tasks)] = None):
    filtered = [(tid, t) for tid, t in tasks.items() if done is None or t.done == done]
    skip, limit = pagination["skip"], pagination["limit"]
    page = filtered[skip : skip + limit]
    return [TaskOut(task_id=tid, **t.dict()) for tid, t in page]

@private.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskIn, existingtask: Annotated[TaskIn, Depends(get_existing_task)], _: Annotated[str, Depends(verify_api_key)]):
    
    tasks[task_id] = task
    return TaskOut(task_id=task_id, **task.dict())


@private.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, task: Annotated[TaskIn, Depends(get_existing_task)]):
    tasks.pop(task_id)
    return None

