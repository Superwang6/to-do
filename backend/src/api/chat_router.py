import asyncio
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.repository import ChatMessageRepository, TodoRepository
from src.model.chat_message import ChatMessage, message_todo
from src.schema import (
    ApiResponse,
    ChatMessageCreate,
    ChatMessageListRequest,
    ChatMessageResponse,
    ChatTextRequest,
    TodoCreate,
    TodoResponse,
    ok,
)
from src.service.parser_service import ParserService
from src.service.speech_service import SpeechService
from src.service.todo_service import TodoService

router = APIRouter(prefix="/api/chat", tags=["chat"])

speech_service = SpeechService()
parser_service = ParserService()


def _get_todo_service(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TodoService:
    return TodoService(TodoRepository(db, current_user["user_id"]))


def _build_bot_response(text: str, parsed: dict | None, todo_service: TodoService) -> dict:
    if not parsed:
        return {
            "response": "好的，已记录。但我没有识别出具体的待办事项，可以再说得清楚一些吗？",
            "todo_created": False,
            "todo": None,
        }

    try:
        create_kwargs = dict(parsed)
        create_kwargs.setdefault("type", "once")
        create_kwargs.setdefault("recurrence_rule", None)
        todo_obj = todo_service.create(TodoCreate(**create_kwargs))
    except Exception:
        return {
            "response": "抱歉，创建待办时出了点问题，请稍后重试。",
            "todo_created": False,
            "todo": None,
        }

    title = todo_obj.title
    parts = [f"已为你创建待办「{title}」"]
    if todo_obj.type == "recurring" and todo_obj.recurrence_rule:
        freq_names = {"daily": "每天", "weekly": "每周", "monthly": "每月", "yearly": "每年"}
        rule = todo_obj.recurrence_rule
        freq_label = freq_names.get(rule.get("frequency"), "")
        interval = rule.get("interval", 1)
        if interval > 1:
            freq_label = f"每{interval}" + freq_label[1:]
        time_of_day = rule.get("time_of_day")
        if time_of_day:
            freq_label += time_of_day
        parts.append(f"重复：{freq_label}")
    if todo_obj.due_date:
        due = todo_obj.due_date
        if due.hour == 0 and due.minute == 0:
            parts.append(f"截止日期：{due.strftime('%m/%d')}")
        else:
            parts.append(f"截止日期：{due.strftime('%m/%d %H:%M')}")
    if todo_obj.priority == "high":
        parts.append("已标记为重要")

    return {
        "response": "，".join(parts) + "。",
        "todo_created": True,
        "todo": TodoResponse.model_validate(todo_obj),
    }


def _make_bot_msg_resp(bot_msg: ChatMessage, todo) -> dict:
    """Build a dict for ChatMessageResponse with associated todos."""
    return {
        "id": bot_msg.id,
        "role": bot_msg.role,
        "content": bot_msg.content,
        "duration": bot_msg.duration,
        "todo_created": bot_msg.todo_created,
        "todos": [{"id": todo.id, "title": todo.title, "priority": todo.priority, "status": todo.status}] if todo else [],
        "created_at": bot_msg.created_at,
    }


# ──────────────────────────────────────────────
#  Text chat: process text, save bot message, link to todos
# ──────────────────────────────────────────────
@router.post("/text", response_model=ApiResponse)
def chat_text(
    body: ChatTextRequest,
    todo_service: TodoService = Depends(_get_todo_service),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not body.text or not body.text.strip():
        raise HTTPException(400, "text cannot be empty")

    text = body.text.strip()
    parsed = parser_service.parse(text)
    data = _build_bot_response(text, parsed, todo_service)

    # Save bot message
    repo = ChatMessageRepository(db, current_user["user_id"])
    bot_msg = repo.create(ChatMessage(
        role="bot",
        content=data["response"],
        todo_created=data["todo_created"],
    ))

    # Create message-todo association
    todo = data.get("todo")
    if todo:
        db.execute(message_todo.insert().values(message_id=bot_msg.id, todo_id=todo.id))
        db.commit()

    data["bot_message"] = _make_bot_msg_resp(bot_msg, todo)
    return ok(data=data)


# ──────────────────────────────────────────────
#  Audio chat: transcribe, save user message, return transcription
# ──────────────────────────────────────────────
@router.post("/audio", response_model=ApiResponse)
async def chat_audio(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    import logging
    logger = logging.getLogger(__name__)

    ext = os.path.splitext(file.filename)[1] if file.filename else '.mp3'
    if ext not in (".wav", ".mp3", ".m4a", ".ogg"):
        ext = '.mp3'

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    content = await file.read()
    logger.info(f"[Audio] Received file: {file.filename}, ext: {ext}, size: {len(content)} bytes")
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        text = await asyncio.to_thread(speech_service.transcribe, save_path)
        logger.info(f"[Audio] Transcription result: '{text}'")
    except Exception as e:
        logger.error(f"[Audio] Transcription failed: {e}", exc_info=True)
        raise HTTPException(500, f"Transcription failed: {str(e)}")
    finally:
        os.remove(save_path)

    repo = ChatMessageRepository(db, current_user["user_id"])
    user_msg = repo.create(ChatMessage(role="user", content=text))

    return ok(data={
        "transcribed_text": text,
        "user_message": ChatMessageResponse.model_validate(user_msg),
    })


# ──────────────────────────────────────────────
#  Message persistence (generic save + list)
# ──────────────────────────────────────────────
@router.post("/messages/list", response_model=ApiResponse)
def list_messages(
    body: ChatMessageListRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    p = body.page
    base = db.query(ChatMessage).filter(ChatMessage.user_id == current_user["user_id"])
    msgs = (
        base
        .options(joinedload(ChatMessage.todos))
        .order_by(ChatMessage.created_at.asc())
        .offset((p.page - 1) * p.page_size)
        .limit(p.page_size)
        .all()
    )
    total = base.count()
    return ok(
        data=[ChatMessageResponse.model_validate(m) for m in msgs],
        total=total,
    )


@router.post("/messages/save", response_model=ApiResponse)
def save_message(
    body: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    dao = ChatMessageRepository(db, current_user["user_id"])
    msg = dao.create(ChatMessage(
        role=body.role,
        content=body.content,
        duration=body.duration,
        todo_created=body.todo_created,
    ))

    if body.todo_ids:
        for todo_id in body.todo_ids:
            db.execute(message_todo.insert().values(message_id=msg.id, todo_id=todo_id))
        db.commit()
        db.refresh(msg)

    return ok(data=ChatMessageResponse.model_validate(msg))
