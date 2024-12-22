
from telegram import Bot
from telegram.error import TelegramError

from logger_setup import setup_logger
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger()


class TelegramMessenger:
    """
    A class to send unprompted messages to Telegram users.
    """

    def __init__(self, bot_token):
        """
        Initialize the Telegram bot with the provided bot token.
        :param bot_token: str - The Telegram bot token from BotFather.
        """
        self.bot = Bot(token=bot_token)

    def send_message(self, telegram_id, text):
        """
        Send a message to a user.
        :param chat_id: int - The Telegram chat ID of the user.
        :param text: str - The text message to send.
        :return: bool - True if the message was sent successfully, False otherwise.
        """
        try:
            self.bot.send_message(chat_id=telegram_id, text=text)
            logger.debug(f"Message sent to chat ID {telegram_id}: {text}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to chat ID {telegram_id}: {e}")
            return False
