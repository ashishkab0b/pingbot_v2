from dotenv import load_dotenv
import os

load_dotenv()



class Config:
    
    BOT_SECRET_KEY=os.getenv('BOT_SECRET_KEY')
    TELEGRAM_SECRET_KEY=os.getenv('TELEGRAM_SECRET_KEY')
    FRONTEND_BASE_URL="http://localhost:3000"
    
    

class DevelopmentConfig(Config):
    
    DEBUG = True
    FLASK_APP_BOT_BASE_URL="http://localhost:8000/api/bot"
    
    
class ProductionConfig(Config):
        
    DEBUG = False
    FLASK_APP_BOT_BASE_URL="http://flask-backend:8000/api/bot"
        
    
    
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

current_env = os.getenv("ENV_TYPE", "development")
CurrentConfig = config_map.get(current_env, Config)