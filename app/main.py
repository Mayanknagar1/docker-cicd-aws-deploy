"""
Task Manager API
-----------------
A small, purpose-built app for this DevOps demo. It's intentionally simple —
the point of this project is the CI/CD pipeline and deployment, not the app
logic itself. In-memory storage is fine here (no DB needed to demonstrate
containerization + CI/CD + cloud deployment).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Task Manager API", version="1.0.0")

tasks_db = {}
next_id = 1


class Task(BaseModel):
    title: str
    done: bool = False


class TaskOut(Task):
    id: int


@app.get("/health")
def health():
    """Used by the deployment pipeline / load balancer to check the app is alive."""
    return {"status": "ok", "version": os.getenv("APP_VERSION", "dev")}


@app.get("/tasks", response_model=List[TaskOut])
def list_tasks():
    return [TaskOut(id=tid, **t.dict()) for tid, t in tasks_db.items()]


@app.post("/tasks", response_model=TaskOut)
def create_task(task: Task):
    global next_id
    tasks_db[next_id] = task
    out = TaskOut(id=next_id, **task.dict())
    next_id += 1
    return out


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: Task):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db[task_id] = task
    return TaskOut(id=task_id, **task.dict())


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"deleted": task_id}
