from dotenv import load_dotenv
import os

load_dotenv()



class Config:
    
    BOT_SECRET_KEY=os.getenv('BOT_SECRET_KEY')
    TELEGRAM_SECRET_KEY=os.getenv('TELEGRAM_SECRET_KEY')
    
    FLASK_APP_BOT_BASE_URL="http://localhost:8000/api/bot"