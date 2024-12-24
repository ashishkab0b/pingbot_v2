

from telegram import Bot
from config import Config
import asyncio

config = Config()

bot = Bot(token=config.TELEGRAM_SECRET_KEY)

async def send(chat_id, message):
    """
    Send a message to a user.
    :param chat_id: int - The Telegram chat ID of the user.
    :param message: str - The message to send.
    """
    await bot.send_message(chat_id=chat_id, text=message)
    
    return None

if __name__ == "__main__":
    
    chat_id = 1860202072
    message = "hi"
    
    asyncio.run(send(chat_id, message))