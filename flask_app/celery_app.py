# celery_app.py

from celery import Celery
from app import create_app
from celery_factory import make_celery
from config import CurrentConfig

# Create the Flask app using the current configuration
app = create_app(CurrentConfig)

# Create and configure the Celery app
celery = make_celery(app)