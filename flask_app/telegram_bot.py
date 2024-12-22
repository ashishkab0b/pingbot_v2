from flask import Flask, request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import boto3
import re
import os
from telegram.ext import ConversationHandler
from dotenv import load_dotenv
import pytz
import yaml
from backend import Participant, Study
from logger_setup import setup_logger

logger = setup_logger()
load_dotenv()

with open('telegram_msgs.yml', 'r') as file:
    msgs = yaml.safe_load(file)

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_DEFAULT_REGION']
)
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

# Initialize bot
BOT_TOKEN = os.getenv('TELEGRAM_SECRET_KEY')

# Define conversation states
START, AWAIT_TIMEZONE, AWAIT_STUDY_CODE, UNENROLL, VIEW_STUDIES  = range(5)


# Check if study code matches pattern with 8 letter study code and optional study_pid separated by a hyphen
def validate_study_code(study_code): 
    # Define the regular expression
    pattern = r'^[a-z]{8}$|^[a-z]{8}-[a-zA-Z0-9]+$'
    return re.fullmatch(pattern, study_code) is not None

def timezone_keyboard():
    timezones = [
        "America/New_York",    # Eastern Time
        "America/Chicago",     # Central Time
        "America/Denver",      # Mountain Time
        "America/Phoenix",     # Mountain Time (Arizona, no DST)
        "America/Los_Angeles", # Pacific Time
        "America/Anchorage",   # Alaska Time
        "America/Adak",        # Hawaii-Aleutian Time (Aleutian Islands, observes DST)
        "Pacific/Honolulu",    # Hawaii-Aleutian Time (Hawaii, no DST)
        "America/Puerto_Rico", # Atlantic Time (Puerto Rico, U.S. Virgin Islands)
        "Pacific/Pago_Pago",   # Samoa Time (American Samoa)
        "Pacific/Guam",        # Chamorro Time (Guam, Northern Mariana Islands)
    ]
    return ReplyKeyboardMarkup(timezones, one_time_keyboard=True, resize_keyboard=True)


'''
User starts convo with bot
bot sends list of commands

'''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    
    # msgs['start'].format(command_list)
    msg = "Welcome to the study bot! Here are the available commands:\n"

    await update.message.reply_text(msg)

    return START

async def prompt_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please select your timezone.",
        reply_markup=timezone_keyboard()
    )
    return AWAIT_TIMEZONE


async def process_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
     
    timezone = update.message.text
    
    # Check if the timezone is valid
    if timezone not in pytz.all_timezones:
        await update.message.reply_text("Invalid timezone. Please select a valid timezone from the list.",
                                  reply_markup=timezone_keyboard())
        return AWAIT_TIMEZONE
    
    telegram_id = str(update.message.from_user.id)
    context.user_data['timezone'] = timezone
    Participant().update_tz(tz=timezone, telegram_id=telegram_id)
    
    return PROMPT_STUDY_CODE
    
   

async def prompt_study_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user for a study code."""
    telegram_id = str(update.message.from_user.id)
    participant = Participant().get_participant(telegram_id)
    tz = participant.get('tz')
    if not tz:
        return process_timezone(update, context)
    context.user_data['tz'] = tz
    await update.message.reply_text("Please enter the study code given to you by the researcher.")
    return STUDY_CODE


async def process_study_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = str(update.message.from_user.id)
    study_code = update.message.text
    participant = Participant().get_participant(telegram_id)
    
    # Check if the participant has a timezone set
    if not participant or not participant.get('tz'):
        return process_timezone(update, context)
    
    # Check if the study code is valid
    if not validate_study_code(study_code):
        update.message.reply_text("Invalid study code. Please enter a valid study code or type /cancel to cancel.")
        return STUDY_CODE
    
    # Enroll participant
    study_code_parts = study_code.split('-')
    study_pid = study_code_parts[1] if len(study_code_parts) > 1 else None
    study_code = study_code_parts[0]
    study = Study().get_study(study_code)
    study_id = study.study_id
    if not study:
        update.message.reply_text("Study not found. Please enter a valid study code or type /cancel to cancel.")
        return STUDY_CODE
    
    participant.enroll_participant(study_id, study_pid)
    
    return TIMEZONE

def unenroll(update, context):
    pass

def view_studies(update, context):
    pass

def cancel(update, context):
    pass



COMMAND_DESCRIPTIONS = {
    'start': 'Show this message',
    'timezone': 'Set your timezone',
    'enroll': 'Enroll in a study using a study code',
    'unenroll': 'Unenroll from a study',
    'viewstudies': 'View the list of your active studies',
    'cancel': 'Cancel the current operation',
}

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
    entry_points=[
            CommandHandler('start', start),
            CommandHandler('timezone', prompt_timezone),
            CommandHandler('enroll', prompt_study_code),
            CommandHandler('unenroll', unenroll),
            CommandHandler('view', view_studies),
            ],
    
        # I think the following are like if you're in a state, then what do you use to process input
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
            AWAIT_TIMEZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_timezone)],
            AWAIT_STUDY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_study_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()