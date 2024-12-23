import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine.url import URL

load_dotenv()

class Config:
    
    JWT_SECRET_KEY= os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
    
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
    
    # TELEGRAM_BOT_SECRET_KEY = os.environ['BOT_SECRET_KEY']
    TELEGRAM_BOT_NAME = "SurveyPingBot"
    
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
    

class DevelopmentConfig(Config):
    
    DEBUG = True

class ProductionConfig(Config):
    
    DEBUG = False