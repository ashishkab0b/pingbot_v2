from flask import Flask, request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler
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
BOT_TOKEN = os.get_env('TELEGRAM_SECRET_KEY')
bot = Bot(token=BOT_TOKEN)

# Define conversation states
START, TIMEZONE, STUDY_CODE, UNENROLL, VIEW_STUDIES  = range(4)

# Create dispatcher for handling updates
dispatcher = Dispatcher(bot, None, use_context=True)

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

def select_timezone(update, context):
    
    update.message.reply_text(
        "Please select your timezone.",
        reply_markup=timezone_keyboard()
    )
    
    timezone = update.message.text
    
    # Check if the timezone is valid
    if timezone not in pytz.all_timezones:
        update.message.reply_text("Invalid timezone. Please select a valid timezone from the list.")
        return TIMEZONE
    telegram_id = str(update.message.from_user.id)
    context.user_data['timezone'] = timezone
    Participant().update_tz(tz=timezone, telegram_id=telegram_id)
    return STUDY_CODE


def start(update, context):
    # Retrieve commands from the ConversationHandler
    commands = [
        handler.command[0] for handler in conv_handler.entry_points if isinstance(handler, CommandHandler)
    ]
    
    # Format the commands with descriptions
    command_list = "\n".join(
        f"/{command} - {COMMAND_DESCRIPTIONS.get(command, '')}"
        for command in commands
    )
    
    # Send the list of commands to the user
    update.message.reply_text(msgs['start'].format(command_list))
    return START

def enter_study_code(update, context):
    telegram_id = str(update.message.from_user.id)
    participant = Participant().get_participant(telegram_id)
    
    # Check if the participant has a timezone set
    if not participant or not participant.get('tz'):
        return select_timezone(update, context)
    
    study_code = update.message.text
    
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




conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('timezone', select_timezone),
        CommandHandler('enroll', enter_study_code),
        CommandHandler('unenroll', unenroll),
        CommandHandler('view-studies', view_studies),
        ],
    states={
        START: [MessageHandler(Filters.text & ~Filters.command, start)],
        TIMEZONE: [MessageHandler(Filters.text & ~Filters.command, select_timezone)],
        STUDY_CODE: [MessageHandler(Filters.text & ~Filters.command, enter_study_code)],
        UNENROLL: [MessageHandler(Filters.text & ~Filters.command, unenroll)],
        VIEW_STUDIES: [MessageHandler(Filters.text & ~Filters.command, view_studies)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
COMMAND_DESCRIPTIONS = {
    'start': 'Show this message',
    'timezone': 'Set your timezone',
    'enroll': 'Enroll in a study using a study code',
    'unenroll': 'Unenroll from a study',
    'view-studies': 'View the list of your active studies',
    'cancel': 'Cancel the current operation',
}

dispatcher.add_handler(conv_handler)
