from typing import Optional

from sqlalchemy.orm import Session

from src.model import Todo


class TodoRepository:
    def __init__(self, db: Session, user_id: int | None = None):
        self.db = db
        self.user_id = user_id

    def _base_query(self):
        q = self.db.query(Todo)
        if self.user_id is not None:
            q = q.filter(Todo.user_id == self.user_id)
        return q

    def create(self, todo: Todo) -> Todo:
        if self.user_id is not None:
            todo.user_id = self.user_id
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return self._base_query().filter(Todo.id == todo_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        start_time=None,
        end_time=None,
        todo_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> tuple[list[Todo], int]:
        query = self._base_query().filter(Todo.recurring_template_id.is_(None))
        if start_time:
            query = query.filter(Todo.created_at >= start_time)
        if end_time:
            query = query.filter(Todo.created_at <= end_time)
        if todo_type:
            query = query.filter(Todo.type == todo_type)
        if status:
            query = query.filter(Todo.status == status)
        if keyword:
            query = query.filter(Todo.title.contains(keyword))
        total = query.count()
        items = (
            query.order_by(Todo.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    def get_by_template_id(self, template_id: int) -> list[Todo]:
        return (
            self._base_query()
            .filter(Todo.recurring_template_id == template_id)
            .order_by(Todo.created_at.desc())
            .all()
        )

    def get_children_count(self, template_id: int) -> int:
        return (
            self._base_query()
            .filter(Todo.recurring_template_id == template_id)
            .count()
        )

    def update(self, todo_id: int, data: dict) -> Optional[Todo]:
        todo = self.get_by_id(todo_id)
        if not todo:
            return None
        for key, value in data.items():
            setattr(todo, key, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self.get_by_id(todo_id)
        if not todo:
            return False
        self.db.delete(todo)
        self.db.commit()
        return True

    def get_active(self, priority: Optional[str] = None) -> list[Todo]:
        """Return non-completed template todos."""
        query = (
            self._base_query()
            .filter(
                Todo.recurring_template_id.is_(None),
                Todo.status != "completed",
            )
        )
        if priority:
            query = query.filter(Todo.priority == priority)
        return query.all()

    def count_completed(self) -> int:
        """Count all completed todos.

        Includes:
        - Completed once todos (templates)
        - Completed recurring history instances
        """
        return self._base_query().filter(Todo.status == "completed").count()

    def get_completed(self, skip: int = 0, limit: int = 50) -> tuple[list[Todo], int]:
        """Return completed todos with pagination.

        Includes:
        - Completed once todos (templates)
        - Completed recurring history instances (linked to templates)
        """
        query = self._base_query().filter(Todo.status == "completed")
        total = query.count()
        items = (
            query
            .order_by(Todo.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    def delete_cascade(self, todo_id: int) -> bool:
        todo = self.get_by_id(todo_id)
        if not todo:
            return False
        if todo.type == "recurring" and todo.recurring_template_id is None:
            children = self.get_by_template_id(todo_id)
            for child in children:
                self.db.delete(child)
        self.db.delete(todo)
        self.db.commit()
        return True
