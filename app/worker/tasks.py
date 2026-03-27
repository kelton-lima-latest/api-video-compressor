import os
from celery import Celery

# Pega a URL do Redis das variáveis de ambiente (definidas no docker-compose.yml)
# Se não encontrar, usa um valor padrão para evitar quebra (fallback)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inicializa o app do Celery
celery_app = Celery(
    "video_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"] # Diz ao Celery onde procurar as tarefas
)

# Configurações adicionais
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)