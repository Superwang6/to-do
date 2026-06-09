import asyncio
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.repository import TodoRepository
from src.schema import ApiResponse, TodoCreate, TodoResponse, ok
from src.service.parser_service import ParserService
from src.service.speech_service import SpeechService
from src.service.todo_service import TodoService

router = APIRouter(prefix="/api/voice", tags=["voice"])

speech_service = SpeechService()
parser_service = ParserService()


def _get_todo_service(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TodoService:
    return TodoService(TodoRepository(db, current_user["user_id"]))


@router.post("/upload", response_model=ApiResponse)
async def upload_audio(
    file: UploadFile,
    todo_service: TodoService = Depends(_get_todo_service),
):
    ext = os.path.splitext(file.filename)[1] if file.filename else '.mp3'
    if ext not in (".wav", ".mp3", ".m4a", ".ogg"):
        ext = '.mp3'

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        text = await asyncio.to_thread(speech_service.transcribe, save_path)
    except Exception as e:
        raise HTTPException(500, f"Transcription failed: {str(e)}")
    finally:
        os.remove(save_path)

    parsed = parser_service.parse(text)
    todo = None
    if parsed:
        todo_obj = todo_service.create(TodoCreate(**parsed))
        todo = TodoResponse.model_validate(todo_obj)

    return ok(data={"text": text, "todo": todo})
