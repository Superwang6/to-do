from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.repository import TodoRepository
from src.schema import (
    ApiResponse,
    CompletedListResponse,
    GroupedTodoResponse,
    TodoCreate,
    TodoListRequest,
    TodoResponse,
    TodoUpdate,
    ok,
)
from src.service.todo_service import TodoService

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _get_service(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TodoService:
    return TodoService(TodoRepository(db, current_user["user_id"]))


@router.post("/save", response_model=ApiResponse)
def create_todo(data: TodoCreate, service: TodoService = Depends(_get_service)):
    todo = service.create(data)
    return ok(data=TodoResponse.model_validate(todo), message="created")


@router.post("/list", response_model=ApiResponse)
def list_todos(
    body: TodoListRequest,
    service: TodoService = Depends(_get_service),
):
    """Return active todos grouped into today / recurring / once.
    Set body.status='completed' to get completed list instead.
    If keyword is provided, return search result in plain list.
    """
    if body.keyword is not None or body.time_range is not None:
        # Search mode: return plain paginated list with filtering
        p = body.page
        items, total = service.list_all(
            skip=(p.page - 1) * p.page_size,
            limit=p.page_size,
            start_time=body.time_range.start_time if body.time_range else None,
            end_time=body.time_range.end_time if body.time_range else None,
            todo_type=body.type,
            status=body.status,
            keyword=body.keyword,
        )
        data = [TodoResponse.model_validate(item) for item in items]
        return ok(data=data, total=total)

    if body.status == "completed":
        p = body.page
        result = service.list_completed(
            skip=(p.page - 1) * p.page_size,
            limit=p.page_size,
        )
        return ok(data=result.completed, total=result.total)

    grouped = service.list_active(priority=body.priority)
    return ok(data=grouped.model_dump())


@router.get("/detail/{id:int}", response_model=ApiResponse)
def get_todo(id: int, service: TodoService = Depends(_get_service)):
    todo = service.get(id)
    if not todo:
        raise HTTPException(404, "Todo not found")
    return ok(data=TodoResponse.model_validate(todo))


@router.post("/modify/{id:int}", response_model=ApiResponse)
def update_todo(
    id: int,
    data: TodoUpdate,
    service: TodoService = Depends(_get_service),
):
    todo = service.update(id, data)
    if not todo:
        raise HTTPException(404, "Todo not found")
    return ok(data=TodoResponse.model_validate(todo), message="updated")


@router.post("/complete/{id:int}", response_model=ApiResponse)
def complete_todo(id: int, service: TodoService = Depends(_get_service)):
    todo = service.complete(id)
    return ok(data=TodoResponse.model_validate(todo), message="completed")


@router.post("/revert/{id:int}", response_model=ApiResponse)
def revert_completed_todo(id: int, service: TodoService = Depends(_get_service)):
    todo = service.revert_completed(id)
    return ok(data=TodoResponse.model_validate(todo), message="reverted")


@router.post("/delete/{id:int}", response_model=ApiResponse)
def delete_todo(id: int, service: TodoService = Depends(_get_service)):
    if not service.delete(id):
        raise HTTPException(404, "Todo not found")
    return ok(message="deleted")
