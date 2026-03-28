from celery import Celery
from app.core.config import settings

# Agora o Celery pega a URL do Redis direto da classe Settings (que lê do .env)
celery_app = Celery(
    "video_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)