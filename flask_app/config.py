import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine.url import URL
from celery.schedules import crontab

load_dotenv()

class BaseConfig:
    

    MAIL_SERVER = 'live.smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAILTRAP_API_TOKEN = os.environ['MAILTRAP_API_TOKEN']
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_SUPPORT_RECIPIENT = os.environ['MAIL_SUPPORT_RECIPIENT']
    
    JWT_SECRET_KEY= os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    
    TELEGRAM_SECRET_KEY = os.environ['TELEGRAM_SECRET_KEY']
    TELEGRAM_BOT_NAME = "SurveyPingBot"
    MY_TELEGRAM_ID = os.environ['MY_TELEGRAM_ID']
    BOT_USER_AGENTS = ['TelegramBot']
    
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = 0
    
    BOT_SECRET_KEY = os.environ['BOT_SECRET_KEY']
    BOT_ACCOUNT_EMAIL = os.environ['BOT_ACCOUNT_EMAIL']
    BOT_ACCOUNT_PASSWORD = os.environ['BOT_ACCOUNT_PASSWORD']
    
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'options': '-csearch_path=public'}}
    
    CELERY_BEAT_SCHEDULE = {
        'check_and_send_pings': {
            'task': 'tasks.check_and_send_pings',
            'schedule': crontab(minute='*/1'),  # Every minute
        },
    }

    
    TELEGRAM_LINK_CODE_EXPIRY_DAYS = 1
    ENROLLMENT_DASHBOARD_OTP_EXPIRY_MINS = 60
    
    ROLE_PERMISSIONS = {
        "owner": {"share", "edit", "view"},
        "editor": {"edit", "view"},
        "viewer": {"view"},
    }
    
    PING_DEFAULT_URL_TEXT = "Click here to take the survey."
    PING_EXPIRED_MESSAGE = "This ping has expired. Please be sure to take the survey as soon as possible after receiving."
    RECAPTCHA_SECRET_KEY = os.environ['RECAPTCHA_SECRET_KEY']

class DevelopmentConfig(BaseConfig):
    
    DEBUG = True
    
    REDIS_HOST = "localhost"
    REDIS_PASSWORD = None
    REDIS_URL = f"redis://{REDIS_HOST}:6379/0"
    
    # TODO: clean this up
    FRONTEND_BASE_URL = "http://localhost:3000"
    BASE_URL = "http://localhost:3000"
    
    # Celery
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:6379/0"
    

class ProductionConfig(BaseConfig):
    
    DEBUG = False
    
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    REDIS_HOST = "redis"
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0"
    
    # TODO: clean this up
    FRONTEND_BASE_URL = "https://emapingbot.com"
    BASE_URL = "https://emapingbot.com"
    
    # Celery
    CELERY_BROKER_URL= f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0"
    CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0"
    
    

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

current_env = os.getenv("FLASK_ENV", "development")
CurrentConfig = config_map.get(current_env, DevelopmentConfig)