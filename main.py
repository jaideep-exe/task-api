from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")

# In-memory "database": a plain list. It resets whenever the server restarts.
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]

# We read request bodies by hand (to return 400 instead of FastAPI's default 422),
# so these tell Swagger UI what the JSON body looks like.
CREATE_BODY = {"requestBody": {"required": True, "content": {"application/json": {"schema": {
    "type": "object",
    "properties": {"title": {"type": "string"}},
    "required": ["title"],
    "example": {"title": "Buy milk"},
}}}}}

UPDATE_BODY = {"requestBody": {"required": True, "content": {"application/json": {"schema": {
    "type": "object",
    "properties": {"title": {"type": "string"}, "done": {"type": "boolean"}},
    "example": {"title": "Buy oat milk", "done": True},
}}}}}


def error(status_code: int, message: str):
    return JSONResponse(status_code=status_code, content={"error": message})


@app.get("/", summary="API info")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
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
    return error(404, f"Task {task_id} not found")


@app.post("/tasks", status_code=201, summary="Create a new task", openapi_extra=CREATE_BODY)
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return error(400, "Request body must be valid JSON")

    title = body.get("title") if isinstance(body, dict) else None
    if not isinstance(title, str) or not title.strip():
        return error(400, "title is required and must be a non-empty string")

    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": next_id, "title": title.strip(), "done": False}
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", summary="Update a task's title and/or done", openapi_extra=UPDATE_BODY)
async def update_task(task_id: int, request: Request):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return error(404, f"Task {task_id} not found")

    try:
        body = await request.json()
    except Exception:
        return error(400, "Request body must be valid JSON")

    if not isinstance(body, dict) or ("title" not in body and "done" not in body):
        return error(400, "Provide title and/or done")

    if "title" in body and (not isinstance(body["title"], str) or not body["title"].strip()):
        return error(400, "title must be a non-empty string")
    if "done" in body and not isinstance(body["done"], bool):
        return error(400, "done must be true or false")

    # Validate everything first, then change the task, so a bad body never half-updates it.
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
    return error(404, f"Task {task_id} not found")