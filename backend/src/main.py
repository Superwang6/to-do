import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth_router, chat_router, todo_router, user_router, voice_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Todo App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(todo_router.router)
app.include_router(voice_router.router)
app.include_router(chat_router.router)


@app.on_event("startup")
def init_db():
    from src.database import engine
    from src.model import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning("Database not available: %s", e)
        logger.warning("Server started without database. Configure .env and restart.")


@app.get("/api/health")
def health():
    return {"status": "ok"}
