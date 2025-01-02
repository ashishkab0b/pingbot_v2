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
from config import CurrentConfig

# Setup logging
logger = setup_logger()

# Load environment variables
load_dotenv()

# Load configuration
config = CurrentConfig()

# Define conversation states
ENTERING_LINK_CODE = 1

# Define command descriptions
COMMAND_DESCRIPTIONS = {
    'start': 'Show this message',
    'enroll': 'Enroll in a new study',
    'contact': 'Contact the study team',
    # 'dashboard': 'View the online dashboard',
    # 'unenroll': 'Unenroll from a study',
    # 'timezone': 'Set your time zone',
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
        "X-Bot-Secret-Key": config.BOT_SECRET_KEY,
    }
    payload = {
        "telegram_id": update.message.from_user.id,
        "telegram_link_code": linking_code,
    }
    resp = requests.put(f"{config.FLASK_APP_BOT_BASE_URL}/link_telegram_id", json=payload, headers=header)
    logger.debug(f"Status code from link_telegram_id: {resp.status_code}")
    # Handle telegram ID already linked
    if resp.status_code == 409:
        msg = "This Telegram account is already linked to the study. Please contact the researcher for assistance."
        await update.message.reply_text(msg)
        return
    
    # Catch all
    if resp.status_code != 200:
        msg = "An error occurred. Please try again or type /cancel to cancel."
        logger.error(f"Error linking Telegram ID to enrollment with status code: {resp.status_code}")
        await update.message.reply_text(msg)
        return ENTERING_LINK_CODE
    
    msg = "You have been successfully enrolled in the study."
    await update.message.reply_text(msg)
    return ConversationHandler.END


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /dashboard command."""
    header = {
        "X-Bot-Secret-Key": config.BOT_SECRET_KEY,
    }
    payload = {
        "telegram_id": update.message.from_user.id,
    }
    url = f"{config.FLASK_APP_BOT_BASE_URL}/participant_login"
    logger.debug(f"Sending dashboard login request to {url} with telegramID={update.message.from_user.id}")
    resp = requests.post(url=url, json=payload, headers=header)
    
    if resp.status_code != 200:
        msg = "An error occurred. Please try again later."
        logger.error(f"Error with participant_login endpoint. Status code: {resp.status_code}")
        await update.message.reply_text(msg)
        return
    
    
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /contact command."""
    
    # Prepare the request
    header = {
        "X-Bot-Secret-Key": config.BOT_SECRET_KEY,
    }
    payload = {
        "telegram_id": update.message.from_user.id,
    }

    url = f"{config.FLASK_APP_BOT_BASE_URL}/get_contact_msgs"
    
    logger.debug(f"Sending contact message GET request to {url} with telegramID={update.message.from_user.id}")

    # Send the request
    resp = requests.get(url=url, params=payload, headers=header)
    
    # Handle errors
    if resp.status_code != 200:
        msg = "An error occurred. Please try again later."
        logger.error(f"Error with participant_contact endpoint. Status code: {resp.status_code}")
        await update.message.reply_text(msg)
        return
    
    # Handle success
    for study in resp.json():
        msg = f"Study: {study['public_name']}\nContact: {study['contact_message']}"
        await update.message.reply_text(msg)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /cancel command."""
    msg = "Operation canceled. Returning to the main menu."
    
    await update.message.reply_text(msg)
    await start(update, context)
    return ConversationHandler.END

# Define a fallback handler for unclassified messages
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback handler for unrecognized messages."""
    await start(update, context)

def main() -> None:
    """Main function to start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(config.TELEGRAM_SECRET_KEY).build()

    # Define a conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('enroll', enroll),
            CommandHandler('contact', contact),
            # CommandHandler('dashboard', dashboard),
            # CommandHandler('unenroll', dashboard),
        ],
        states={
            ENTERING_LINK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, entering_link_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))  # Independent start command
    application.add_handler(conv_handler)
    
    # Add a fallback handler to catch unclassified messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()