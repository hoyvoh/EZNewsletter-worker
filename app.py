from celery import Celery
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from celery.schedules import crontab
from dotenv import load_dotenv
load_dotenv()

celery = Celery(__name__)

celery.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND'),
    timezone='UTC',
    enable_utc=True,
)

celery.autodiscover_tasks(['emails'])
celery.conf.worker_force_execv = False

celery.conf.beat_schedule = {
    'send-newsletter-daily': {
        'task': 'emails.send_newsletter',
        'schedule': crontab(hour=8, minute=0),  
    },
}

@celery.task
def test_celery():
    return "Test Celery Task Executed Successfully"
