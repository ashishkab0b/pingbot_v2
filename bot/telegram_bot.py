from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import os
import yaml
from dotenv import load_dotenv
from logger_setup import setup_logger
import requests
# from app import db

# Setup logging
logger = setup_logger()

# Load environment variables
load_dotenv()

# Initialize bot
BOT_TOKEN = os.getenv('TELEGRAM_SECRET_KEY')

# Define conversation states
ENTERING_LINK_CODE = 1

# Define command descriptions
COMMAND_DESCRIPTIONS = {
    'start': 'Show this message',
    'dashboard': 'Generate a one-time login link to the online dashboard',
    'enroll': 'Enroll in a study',
    'unenroll': 'Unenroll from a study',
}

# Define the conversation handler functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and displays available commands."""
    msg = "Welcome to the study bot! Here are the available commands:\n"
    for command, description in COMMAND_DESCRIPTIONS.items():
        msg += f"/{command}: {description}\n"
    await update.message.reply_text(msg)


async def enroll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /enroll command and prompts for a signup code."""
    msg = "Please enter the signup code for the study you would like to enroll in."
    await update.message.reply_text(msg)
    return ENTERING_LINK_CODE


async def entering_link_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the input of a study signup code."""
    linking_code = update.message.text.strip()
    header = {
        "X-Bot-Secret-Key": os.getenv('BOT_SECRET_KEY'),
    }
    payload = {
        "telegram_id": update.message.from_user.id,
        "telegram_link_code": linking_code,
    }
    resp = requests.put(f"{os.getenv('FLASK_APP_BOT_BASE_URL')}/link_telegram_id", json=payload, headers=header)
    if resp.status_code != 200:
        msg = "An error occurred. Please try again or type /cancel to cancel."
        logger.error(f"Error linking Telegram ID to enrollment with status code: {resp.status_code}")
        await update.message.reply_text(msg)
        return ENTERING_LINK_CODE
    
    msg = "You have been successfully enrolled in the study."
    await update.message.reply_text(msg)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /cancel command."""
    msg = "Operation canceled. Returning to the main menu."
    
    await update.message.reply_text(msg)
    await start(update, context)
    return ConversationHandler.END


def main() -> None:
    """Main function to start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Define a conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('enroll', enroll),
        ],
        states={
            ENTERING_LINK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, entering_link_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))  # Independent start command
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()