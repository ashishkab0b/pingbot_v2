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
import requests
from dotenv import load_dotenv
from logger_setup import setup_logger
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
    'contact': 'View instructions for contacting the study team',
    'dashboard': 'View the online dashboard',
    # 'unenroll': 'Unenroll from a study',
    # 'timezone': 'Set your time zone',
}

# --- Handlers ---
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
    resp = requests.put(
        f"{config.FLASK_APP_BOT_BASE_URL}/link_telegram_id",
        json=payload,
        headers=header
    )
    logger.debug(f"Status code from link_telegram_id: {resp.status_code}")

    if resp.status_code == 409:
        msg = (
            "This Telegram account is already linked to the study. "
            "Please contact the researcher for assistance."
        )
        await update.message.reply_text(msg)
        return ConversationHandler.END

    if resp.status_code != 200:
        msg = "An error occurred. Please try again or type /cancel to cancel."
        logger.error(
            f"Error linking Telegram ID to enrollment: {resp.status_code}"
        )
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
    logger.debug(
        f"Sending dashboard login request to {url} with telegramID={update.message.from_user.id}"
    )
    resp = requests.post(url=url, json=payload, headers=header)

    if resp.status_code != 200:
        msg = "An error occurred. Please try again later."
        logger.error(
            f"Error with participant_login endpoint. Status code: {resp.status_code}"
        )
        await update.message.reply_text(msg)
        return


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /contact command."""
    header = {
        "X-Bot-Secret-Key": config.BOT_SECRET_KEY,
    }
    payload = {
        "telegram_id": update.message.from_user.id,
    }

    url = f"{config.FLASK_APP_BOT_BASE_URL}/get_contact_msgs"
    logger.debug(
        f"Sending contact message GET request to {url} with telegramID={update.message.from_user.id}"
    )
    resp = requests.get(url=url, params=payload, headers=header)

    if resp.status_code != 200:
        msg = "An error occurred. Please try again later."
        logger.error(
            f"Error with participant_contact endpoint. Status code: {resp.status_code}"
        )
        await update.message.reply_text(msg)
        return

    for study in resp.json():
        msg = f"Study: {study['public_name']}\nContact: {study['contact_message']}"
        await update.message.reply_text(msg)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /cancel command."""
    msg = "Operation canceled. Returning to the main menu."
    await update.message.reply_text(msg)
    await start(update, context)
    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback handler for unrecognized messages."""
    await start(update, context)


def main() -> None:
    """Main function to start the bot in webhook mode."""
    # Build the Application with your bot token
    application = Application.builder().token(config.TELEGRAM_SECRET_KEY).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('enroll', enroll),
            CommandHandler('contact', contact),
            CommandHandler('dashboard', dashboard),
            # CommandHandler('unenroll', some_handler),
        ],
        states={
            ENTERING_LINK_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, entering_link_code)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # ---------------------------------------------------------------------------------
    # RUN WEBHOOK INSTEAD OF POLLING
    # ---------------------------------------------------------------------------------
    application.run_webhook(
        listen='0.0.0.0',               # Listen on all network interfaces
        port=8443,                      # Container port to match your docker-compose
        url_path='webhook',            # Must match /webhook/ in nginx.conf location
        webhook_url='https://emapingbot.com/webhook',  # Full public webhook URL
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()