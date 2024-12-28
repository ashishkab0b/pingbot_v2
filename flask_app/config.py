import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine.url import URL

load_dotenv()

class Config:
    
    JWT_SECRET_KEY= os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    
    TELEGRAM_SECRET_KEY = os.environ['TELEGRAM_SECRET_KEY']
    TELEGRAM_BOT_NAME = "SurveyPingBot"
    MY_TELEGRAM_ID = os.environ['MY_TELEGRAM_ID']
    
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = 0
    
    BOT_SECRET_KEY = os.environ['BOT_SECRET_KEY']
    BOT_ACCOUNT_EMAIL = os.environ['BOT_ACCOUNT_EMAIL']
    BOT_ACCOUNT_PASSWORD = os.environ['BOT_ACCOUNT_PASSWORD']
    
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'options': '-csearch_path=public'}}

    
    TELEGRAM_LINK_CODE_EXPIRY_DAYS = 1
    ENROLLMENT_DASHBOARD_OTP_EXPIRY_MINS = 60
    
    ROLE_PERMISSIONS = {
        "owner": {"share", "edit", "view"},
        "editor": {"edit", "view"},
        "viewer": {"view"},
    }
    
    PING_DEFAULT_URL_TEXT = "Click here to take the survey."
    PING_EXPIRED_MESSAGE = "This ping has expired. Please be sure to take the survey as soon as possible after receiving."

class DevelopmentConfig(Config):
    
    DEBUG = True
    
    REDIS_HOST = "localhost"
    REDIS_PASSWORD = None
    
    
    PING_LINK_BASE_URL="http://localhost:8000"
    

class ProductionConfig(Config):
    
    DEBUG = False
    
    REDIS_HOST = "redis"
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    
    
    PING_LINK_BASE_URL="http://localhost:8000"
    
    

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

current_env = os.getenv("FLASK_ENV", "development")
CurrentConfig = config_map.get(current_env, Config)