from dotenv import load_dotenv
import os

load_dotenv()



class Config:
    
    BOT_SECRET_KEY=os.getenv('BOT_SECRET_KEY')
    TELEGRAM_SECRET_KEY=os.getenv('TELEGRAM_SECRET_KEY')
    
    

class DevelopmentConfig(Config):
    
    DEBUG = True
    FRONTEND_BASE_URL="http://localhost:3000"
    FLASK_APP_BOT_BASE_URL="http://localhost:8000/api/bot"
    
    
class ProductionConfig(Config):
        
    DEBUG = False
    FRONTEND_BASE_URL="http://emapingbot.com"
    FLASK_APP_BOT_BASE_URL="http://emapingbot.com/api/bot"
        
    
    
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

current_env = os.getenv("ENV_TYPE", "development")
CurrentConfig = config_map.get(current_env, Config)