from datetime import date, datetime, timezone
from typing import Optional

from fastapi import HTTPException

from src.model import Todo
from src.repository import TodoRepository
from src.schema import CompletedListResponse, GroupedTodoResponse, TodoCreate, TodoResponse, TodoUpdate
from src.util.date_util import calculate_first_due_date, calculate_next_due_date

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _sort_key(todo: Todo):
    """Sort by due_date (asc, None last), then priority (high first)."""
    if todo.due_date is None:
        date_val = 1  # None sorts last
        date_key = (1, "")
    else:
        date_val = 0
        date_key = (0, todo.due_date.isoformat())
    prio = PRIORITY_ORDER.get(todo.priority, 1)
    return (date_val, date_key, prio)


def _is_today_or_past(d: datetime) -> bool:
    """Check if a datetime is today or past, using UTC time for consistency."""
    if d is None:
        return False
    today_utc = datetime.now(timezone.utc).date()
    due_date = d.date() if isinstance(d, datetime) else d
    return due_date <= today_utc


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def create(self, data: TodoCreate) -> Todo:
        create_dict = data.model_dump(exclude={"recurrence_rule"})
        if data.recurrence_rule:
            rule_dict = data.recurrence_rule.model_dump()
            create_dict["recurrence_rule"] = rule_dict
            if data.type == "recurring" and not data.due_date:
                create_dict["due_date"] = calculate_first_due_date(
                    rule_dict, time_of_day=rule_dict.get("time_of_day")
                )
        elif data.type == "recurring" and not data.due_date:
            create_dict["due_date"] = calculate_first_due_date({})
        return self.repository.create(Todo(**create_dict))

    def get(self, todo_id: int) -> Optional[Todo]:
        return self.repository.get_by_id(todo_id)

    def list_active(self, priority: Optional[str] = None) -> GroupedTodoResponse:
        """Return active todos grouped into today / recurring / once."""
        todos = self.repository.get_active(priority=priority)
        today, recurring, once = [], [], []

        for t in todos:
            if t.due_date and _is_today_or_past(t.due_date):
                today.append(t)
            elif t.type == "recurring":
                recurring.append(t)
            else:
                once.append(t)

        for group in [today, recurring, once]:
            group.sort(key=_sort_key)

        return GroupedTodoResponse(
            today=[TodoResponse.model_validate(t) for t in today],
            recurring=[TodoResponse.model_validate(t) for t in recurring],
            once=[TodoResponse.model_validate(t) for t in once],
            completed_count=self.repository.count_completed(),
        )

    def list_completed(self, skip: int = 0, limit: int = 50) -> CompletedListResponse:
        """Return completed todos, paginated."""
        items, total = self.repository.get_completed(skip=skip, limit=limit)
        return CompletedListResponse(
            completed=[TodoResponse.model_validate(t) for t in items],
            total=total,
        )

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        start_time=None,
        end_time=None,
        todo_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> tuple[list[Todo], int]:
        return self.repository.get_all(
            skip, limit, start_time, end_time, todo_type, status, keyword
        )

    def update(self, todo_id: int, data: TodoUpdate) -> Optional[Todo]:
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        # Type cannot be changed
        if "type" in update_dict:
            del update_dict["type"]
        if "recurrence_rule" in update_dict and update_dict["recurrence_rule"]:
            update_dict["recurrence_rule"] = update_dict["recurrence_rule"].model_dump()
        return self.repository.update(todo_id, update_dict)

    def complete(self, todo_id: int) -> Todo:
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            raise HTTPException(404, "Todo not found")

        if todo.type == "once":
            if todo.status == "completed":
                raise HTTPException(400, "Todo is already completed")
            return self.repository.update(todo_id, {"status": "completed"})

        # Recurring
        if todo.recurring_template_id is not None:
            raise HTTPException(400, "请完成当前周期的事项")

        if todo.status == "completed":
            raise HTTPException(400, "Todo is already completed")

        # 1. Create completed history instance
        # 历史实例的截止日期记录为今天（实际完成的日期）
        # 而不是原模板的过期截止日期
        today = datetime.now(timezone.utc).date()
        completed_due_date = (
            datetime.combine(today, todo.due_date.time())
            if todo.due_date
            else None
        )
        history = Todo(
            title=todo.title,
            description=todo.description,
            due_date=completed_due_date,
            priority=todo.priority,
            status="completed",
            type="recurring",
            recurrence_rule=todo.recurrence_rule,
            recurring_template_id=todo.id,
        )
        self.repository.create(history)

        # 2. Advance template due_date
        # 从今天开始计算下一个截止日期，而不是从原截止日期开始
        # 避免过期多日的事项完成后仍停留在今天分类
        current_due_date = todo.due_date.date()

        if current_due_date < today:
            # 截止日期已过期，从今天开始计算下一次
            next_due = calculate_next_due_date(
                datetime.combine(today, todo.due_date.time()),
                todo.recurrence_rule
            )
        else:
            # 截止日期是今天或未来，正常顺延
            next_due = calculate_next_due_date(todo.due_date, todo.recurrence_rule)
        self.repository.update(todo.id, {"due_date": next_due})

        self.repository.db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            return False
        if todo.type == "recurring" and todo.recurring_template_id is None:
            return self.repository.delete_cascade(todo_id)
        return self.repository.delete(todo_id)

    def revert_completed(self, todo_id: int) -> Todo:
        """Revert a completed todo back to pending."""
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            raise HTTPException(404, "Todo not found")
        if todo.recurring_template_id is not None:
            raise HTTPException(400, "不能重复激活历史周期实例")
        if todo.status != "completed":
            raise HTTPException(400, "只能恢复已完成的待办")
        return self.repository.update(todo_id, {"status": "pending"})
