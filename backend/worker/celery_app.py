from celery import Celery
from backend.config.settings import settings

celery_app = Celery(
    "openintel_worker",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
    include=["backend.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
