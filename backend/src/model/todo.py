from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from src.model.base import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum("low", "medium", "high", name="priority_enum"), default="medium")
    status = Column(Enum("pending", "completed", name="status_enum"), default="pending")
    type = Column(Enum("once", "recurring", name="todo_type_enum"), default="once", nullable=False)
    recurrence_rule = Column(JSON, nullable=True)
    recurring_template_id = Column(Integer, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    template = relationship(
        "Todo",
        remote_side=[id],
        primaryjoin="Todo.recurring_template_id == Todo.id",
        foreign_keys=[recurring_template_id],
        backref="instances",
    )
