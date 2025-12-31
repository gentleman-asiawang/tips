from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import os, shutil, time
from django.conf import settings
import logging
import datetime

logger = logging.getLogger("apps")

def clean_uuid_tmp():
    temp_dir = settings.TEMP_DIR
    ttl = 24*3600
    now = time.time()
    now_str = datetime.datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Start Cleaner at: {now_str}")
    if not os.path.exists(temp_dir):
        return
    for dirname in os.listdir(temp_dir):
        path = os.path.join(temp_dir, dirname)
        if os.path.isdir(path) and now - os.path.getmtime(path) > ttl:
            try:
                shutil.rmtree(path)
                logger.info(f"Deleted {path}")
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")


class ApiTestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tips'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        scheduler = BackgroundScheduler()
        scheduler.add_job(clean_uuid_tmp, 'interval', days=3)
        scheduler.start()

