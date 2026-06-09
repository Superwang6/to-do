from src.model.chat_message import ChatMessage
from sqlalchemy.orm import Session


class ChatMessageRepository:
    def __init__(self, db: Session, user_id: int | None = None):
        self.db = db
        self.user_id = user_id

    def _base_query(self):
        q = self.db.query(ChatMessage)
        if self.user_id is not None:
            q = q.filter(ChatMessage.user_id == self.user_id)
        return q

    def create(self, msg: ChatMessage) -> ChatMessage:
        if self.user_id is not None:
            msg.user_id = self.user_id
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_all(self, skip: int = 0, limit: int = 200) -> tuple[list[ChatMessage], int]:
        q = self._base_query()
        total = q.count()
        items = (
            q.order_by(ChatMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total
