
from telegram import Bot
from telegram.error import TelegramError
import asyncio

from logger_setup import setup_logger
from dotenv import load_dotenv
from flask import request, jsonify, Blueprint, current_app
from app import db
from models import Ping, PingTemplate, Study, Enrollment

load_dotenv()

logger = setup_logger()


class MessageConstructor:
    """
    A class to send unprompted messages to Telegram users.
    """
    URL_VARIABLES = {
        "<PING_ID>": {
            "description": "The ID of the ping in the database.",
            "db_table": "pings",
            "db_column": "id",
        },
        "<REMINDER_TIME>": {
            "description": "The time at which the reminder will be sent.",
            "db_table": "pings",
            "db_column": "reminder_ts",
        },
        "<SCHEDULED_TIME>": {
            "description": "The time at which the ping is scheduled to be sent.",
            "db_table": "pings",
            "db_column": "scheduled_ts",
        },
        "<EXPIRE_TIME>": {
            "description": "The time at which the ping will expire.",
            "db_table": "pings",
            "db_column": "expire_ts",
        },
        "<DAY_NUM>": {
            "description": "The day number of the ping (Day 0 is date of participant signup).",
            "db_table": "pings",
            "db_column": "day_num",
        },
        "<PING_TEMPLATE_ID>": {
            "description": "The ID of the ping template in the database.",
            "db_table": "ping_templates",
            "db_column": "id",
        },
        "<PING_TEMPLATE_NAME>": {
            "description": "The name of the ping template.",
            "db_table": "ping_templates",
            "db_column": "name",
        },
        "<STUDY_ID>": {
            "description": "The ID of the study in the database.",
            "db_table": "studies",
            "db_column": "id",
        },
        "<STUDY_PUBLIC_NAME>": {
            "description": "The public name of the study.",
            "db_table": "studies",
            "db_column": "public_name",
        },
        "<STUDY_INTERNAL_NAME>": {
            "description": "The internal name of the study.",
            "db_table": "studies",
            "db_column": "internal_name",
        },
        "<STUDY_CONTACT_MSG>": {
            "description": "The contact message for the study.",
            "db_table": "studies",
            "db_column": "contact_message",
        },
        "<PID>": {
            "description": "The researcher-assigned participant ID.",
            "db_table": "enrollments",
            "db_column": "study_pid",
        },
        "<ENROLLMENT_ID>": {
            "description": "The ID of the enrollment in the database.",
            "db_table": "enrollments",
            "db_column": "id",
        },
        "<ENROLLMENT_START_DATE>": {
            "description": "The date the participant enrolled in the study.",
            "db_table": "enrollments",
            "db_column": "start_date",
        },
        "<PR_COMPLETED>": {
            "description": "The proportion of completed pings out of sent pings (i.e., excluding future pings).",
            "db_table": "enrollments",
            "db_column": "pr_completed",
        },
    }

    MESSAGE_VARIABLES = URL_VARIABLES | {
        "<URL>": {
            "description": "The URL to include in the message.",
            "db_table": "pings",
            "db_column": "url",
        },
    }
    
    def __init__(self, ping: Ping):
        """
        Initialize the Telegram bot with the provided bot token.
        :param bot_token: str - The Telegram bot token from BotFather.
        :param ping_id: int - The ID of the ping in the database.
        """
        
        self.ping = ping
        self.telegram_id = self.ping.enrollment.telegram_id
        self.url = None
        self.message = None
        
    def construct_url(self):
        """
        Construct a URL for a ping.
        :return: str - The URL for the ping.
        """
        url = self.ping.url
        for key, value in self.URL_VARIABLES.items():
            if value['db_table'] == 'pings':
                url = url.replace(key, str(getattr(self.ping, value['db_column'])))
            elif value['db_table'] == 'studies':
                url = url.replace(key, str(getattr(self.ping.enrollment.study, value['db_column'])))
            elif value['db_table'] == 'ping_templates':
                url = url.replace(key, str(getattr(self.ping.ping_template, value['db_column'])))
            elif value['db_table'] == 'enrollments':
                url = url.replace(key, str(getattr(self.ping.enrollment, value['db_column'])))
        
        self.url = url
        return url
        
    def construct_message(self):
        """
        Construct a message with a URL.
        :return: str - The message with the URL.
        """

        message = self.ping.message or ""  # TODO: will be removed after fixing message model to non nullable
            
        if not self.ping.message and not self.ping.url: # TODO: will be removed after fixing message model to non nullable
            message = 'MISSING MESSAGE'
        
        replace_url = True if "<URL>" in message else False
        
        for key, value in self.MESSAGE_VARIABLES.items():
            if value['db_table'] == 'pings':
                message = message.replace(key, str(getattr(self.ping, value['db_column'])))
            elif value['db_table'] == 'studies':
                message = message.replace(key, str(getattr(self.ping.enrollment.study, value['db_column'])))
            elif value['db_table'] == 'ping_templates':
                message = message.replace(key, str(getattr(self.ping.ping_template, value['db_column'])))
            elif value['db_table'] == 'enrollments':
                message = message.replace(key, str(getattr(self.ping.enrollment, value['db_column']))) 
        
        self.message = message
        return message
    
    
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
            await self.bot.send_message(chat_id=telegram_id, text=message)
            return None
        
        try:
            asyncio.run(send(telegram_id, message))
        except TelegramError as e:
            logger.error(f"Failed to send message to chat ID {telegram_id}")
            logger.exception(e)
            return False
        else:
            logger.info(f"Successfully sent message to chat ID {telegram_id}")
            return True
        
        