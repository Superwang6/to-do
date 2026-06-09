from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from src.model.base import Base

message_todo = Table(
    "message_todo",
    Base.metadata,
    Column("message_id", Integer, primary_key=True),
    Column("todo_id", Integer, primary_key=True),
    Column("created_at", DateTime, default=datetime.now),
)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    todo_created = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    todos = relationship(
        "Todo",
        secondary=message_todo,
        primaryjoin="ChatMessage.id == message_todo.c.message_id",
        secondaryjoin="Todo.id == message_todo.c.todo_id",
        backref="messages",
    )
