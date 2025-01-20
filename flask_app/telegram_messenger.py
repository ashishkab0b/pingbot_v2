
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio

from logger_setup import setup_logger
from flask import request, jsonify, Blueprint, current_app
from extensions import db
from models import Ping, PingTemplate, Study, Enrollment
import requests

logger = setup_logger()

    
class TelegramMessenger:
    
    def __init__(self, bot_token):
        self.bot_token = bot_token
    
    def send_ping(self, telegram_id, message):
        """
        Send a message to a user using the Telegram Bot HTTP API synchronously.
        :param telegram_id: int - The Telegram chat ID of the user.
        :param message: str - The text message to send.
        :return: bool - True if the message was sent successfully, False otherwise.
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": telegram_id,
            "text": message,
            "parse_mode": "html",
            "link_preview_options": {"is_disabled": True},
            # "disable_web_page_preview": True,
        }

        try:
            # Make a synchronous HTTP POST request
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                # Telegram responds with JSON like {"ok": true, "result": {...}}
                # You could also check response.json()["ok"] for further validation
                logger.info(f"Successfully sent message to telegramID={telegram_id}")
                return True
            else:
                logger.error(
                    f"Failed to send message to telegramID={telegram_id}. "
                    f"Status Code: {response.status_code}, Response: {response.text}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Failed to send message to telegramID={telegram_id}")
            logger.exception(e)
            return False

# class TelegramMessenger:
    
#     def __init__(self, bot_token):
#         self.bot = Bot(token=bot_token)
            
    # def send_ping(self, telegram_id, message):
    #     """
    #     Send a message to a user.
    #     :param telegram_id: int - The Telegram chat ID of the user.
    #     :param text: str - The text message to send.
    #     :return: bool - True if the message was sent successfully, False otherwise.
    #     """
        
    #     async def send(telegram_id, message):
    #         await self.bot.send_message(chat_id=telegram_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    #         return None
        
    #     try:
    #         asyncio.run(send(telegram_id, message))
    #     except TelegramError as e:
    #         logger.error(f"Failed to send message to telegramID={telegram_id}")
    #         logger.exception(e)
    #         return False
    #     else:
    #         logger.info(f"Successfully sent message to telegramID={telegram_id}")
    #         return True
        
    
if __name__ == "__main__":
    import sys
    bot_token = sys.argv[1]
    telegram_messenger = TelegramMessenger(bot_token)
    telegram_id = int(sys.argv[2])
    message = sys.argv[3]
    msg = telegram_messenger.send_ping(telegram_id, message)
    print(msg)
    
