
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio

from logger_setup import setup_logger
from flask import request, jsonify, Blueprint, current_app
from extensions import db
from models import Ping, PingTemplate, Study, Enrollment


logger = setup_logger()

    
class TelegramMessenger:
    
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        
    def send_ping(self, telegram_id, message):
        """
        Send a message to a user.
        :param telegram_id: int - The Telegram chat ID of the user.
        :param text: str - The text message to send.
        :return: bool - True if the message was sent successfully, False otherwise.
        """
        
        async def send(telegram_id, message):
            await self.bot.send_message(chat_id=telegram_id, text=message, parse_mode=ParseMode.HTML)
            return None
        
        try:
            asyncio.run(send(telegram_id, message))
        except TelegramError as e:
            logger.error(f"Failed to send message to telegramID={telegram_id}")
            logger.exception(e)
            return False
        else:
            logger.info(f"Successfully sent message to telegramID={telegram_id}")
            return True
        
        