from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

settings = settings
celery_app = Celery(
    "checker",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}",
    include=["checker.tasks"],
)
celery_app.config_from_object("checker.config")
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.beat_schedule = {
    "run-me-every-minute": {
        "task": "checker.tasks.check",
        "schedule": crontab(minute="*"),
    },
    "run-me-every-minute-2": {
        "task": "checker.tasks.update_predicts_for_records",
        "schedule": crontab(minute="*"),
    },
}
# Дополнительная конфигурация, см. руководство пользователя.
celery_app.conf.update(
    result_expires=3600,
)
