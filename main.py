from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must be valid JSON"}
        )

    title = body.get("title") if isinstance(body, dict) else None

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "title is required and must be a non-empty string"
            }
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1

    task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done")
async def update_task(task_id: int, request: Request):
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must be valid JSON"}
        )

    if not isinstance(body, dict) or (
        "title" not in body and "done" not in body
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title and/or done"}
        )

    if "title" in body:
        if not isinstance(body["title"], str) or not body["title"].strip():
            return JSONResponse(
                status_code=400,
                content={"error": "title must be a non-empty string"}
            )

    if "done" in body and not isinstance(body["done"], bool):
        return JSONResponse(
            status_code=400,
            content={"error": "done must be true or false"}
        )

    if "title" in body:
        task["title"] = body["title"].strip()

    if "done" in body:
        task["done"] = body["done"]

    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )
