from celery import Celery
import os
from dotenv import load_dotenv
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

app = Celery('Tiktok_SAAS')

# Configure Celery to use Redis
app.conf.broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app.conf.result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Automatically discover and register tasks from your 'app' directory.
app.autodiscover_tasks(packages=['app.tasks'])