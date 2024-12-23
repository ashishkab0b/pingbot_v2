from flask import Blueprint, request, g, Response, jsonify, current_app
from flask_jwt_extended import jwt_required
import urllib.parse
from utils import generate_non_confusable_code
from models import Study, Enrollment, Ping, PingTemplate, User
from app import db
from random import randint
from datetime import timedelta, datetime, timezone
import pytz
import secrets
from functools import wraps
from telegram_messenger import TelegramMessenger



bot_bp = Blueprint('bot', __name__)


def bot_auth_required(f):
    """
    Decorator to require bot authentication.
    """
    @wraps(f)  # Preserve the original function's identity
    def wrapper(*args, **kwargs):
        # Check if the request contains the bot secret key
        secret_key = request.headers.get('X-Bot-Secret-Key')
        if not secret_key or secret_key != current_app.config['BOT_SECRET_KEY']:
            current_app.logger.warning(f"Unauthorized attempt to access bot endpoint using secret_key={secret_key}.")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

@bot_bp.route('/link_telegram_id', methods=['PUT'])
@bot_auth_required
def link_telegram_id():
    """
    Link a Telegram ID to a user account.
    """

    # Log the start of the request
    current_app.logger.info("Received request to link Telegram ID.")

    # Get request data
    data = request.get_json()
    secret_key = data.get('secret_key')
    telegram_id = data.get('telegram_id')
    telegram_link_code = data.get('telegram_link_code')

    # Log the received data (excluding sensitive information)
    current_app.logger.debug(f"Request data received: telegram_id={telegram_id}, telegram_link_code={telegram_link_code}")

    # # Check if secret key is correct
    # if secret_key != current_app.config['BOT_SECRET_KEY']:
    #     current_app.logger.warning(f"Unauthorized attempt to link Telegram ID with secret_key={secret_key}.")
    #     return jsonify({"error": "Unauthorized"}), 401

    # Check if required parameters are present
    if not telegram_id:
        current_app.logger.error("Missing telegram_id parameter.")
        return jsonify({"error": "Missing telegram_id parameter."}), 400

    if not telegram_link_code:
        current_app.logger.error("Missing telegram_link_code parameter.")
        return jsonify({"error": "Missing telegram_link_code parameter."}), 400

    # Link Telegram ID to enrollment and mark link code as used
    try:
        current_app.logger.info(f"Attempting to link Telegram ID {telegram_id} with link code {telegram_link_code}.")
        enrollment = Enrollment.query.filter_by(telegram_link_code=telegram_link_code).first()
        if not enrollment:
            current_app.logger.warning(f"No enrollment found for link code {telegram_link_code}.")
            return jsonify({"error": "Invalid telegram_link_code."}), 400
        
        if enrollment.telegram_link_code_used:
            current_app.logger.warning(f"Link code {telegram_link_code} already used.")
            return jsonify({"error": "Invalid telegram_link_code."}), 400

        if enrollment.telegram_link_code_expire_ts < datetime.now(timezone.utc):
            current_app.logger.warning(f"Link code {telegram_link_code} has expired.")
            return jsonify({"error": "Invalid telegram_link_code."}), 400

        enrollment.telegram_id = telegram_id
        enrollment.telegram_link_code_used = True
        db.session.commit()
        current_app.logger.info(f"Successfully linked Telegram ID {telegram_id} to enrollment ID {enrollment.id}.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error linking Telegram ID {telegram_id} to enrollment with link code {telegram_link_code}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error."}), 500

    return jsonify({"message": "Telegram ID linked successfully."}), 200

@bot_bp.route('/unenroll', methods=['PUT'])
@bot_auth_required
def unenroll():
    """
    Unenroll a participant from a study.
    """

    # Log the start of the request
    current_app.logger.info("Received request to unenroll participant.")

    # Get request data
    data = request.get_json()
    telegram_id = data.get('telegram_id')

    # Log the received data (excluding sensitive information)
    current_app.logger.debug(f"Request data received: telegram_id={telegram_id}")

    # Check if required parameters are present
    if not telegram_id:
        current_app.logger.error("Missing telegram_id parameter.")
        return jsonify({"error": "Missing telegram_id parameter."}), 400

    # Unenroll participant
    try:
        current_app.logger.info(f"Attempting to unenroll participant with Telegram ID {telegram_id}.")
        enrollment = Enrollment.query.filter_by(telegram_id=telegram_id).first() # FIX FIX FIX to get for the correct study or all studies
        if not enrollment:
            current_app.logger.warning(f"No enrollment found for Telegram ID {telegram_id}.")
            return jsonify({"error": "Participant not found."}), 404

        enrollment.enrolled = False
        db.session.commit()
        current_app.logger.info(f"Successfully unenrolled participant with Telegram ID {telegram_id}.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unenrolling participant with Telegram ID {telegram_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error."}), 500

    return jsonify({"message": "Participant unenrolled successfully."}), 200


@bot_bp.route('/get_pings_in_time_interval', methods=['GET'])
@bot_auth_required
def get_pings_in_time_interval():
    ''' Query the database and return the pings in a given time interval '''
    
    # Get request data
    data = request.get_json()
    start_ts = data.get('start_ts')
    end_ts = data.get('end_ts')
    
    # Log the start of the request
    current_app.logger.info("Received request to get pings in interval {start_ts} - {end_ts}.")
    
    # Check if required parameters are present
    if not start_ts or not end_ts:
        current_app.logger.error("Missing start_ts or end_ts parameter.")
        return jsonify({"error": "Missing start_ts or end_ts parameter."}), 400
    
    # Convert to datetime objects
    try:
        start_dt = datetime.fromisoformat(start_ts)
        end_dt = datetime.fromisoformat(end_ts)
    except ValueError:
        current_app.logger.error("Invalid datetime format.")
        return jsonify({"error": "Invalid datetime format."}), 400
    
    # Get pings for the date
    try:
        current_app.logger.info(f"Attempting to get pings for interval {start_ts}-{end_ts}.")
        pings = Ping.query.filter(Ping.scheduled_ts >= start_dt, Ping.scheduled_ts <= end_dt).all()
        if not pings:
            current_app.logger.warning(f"No pings found.")
        current_app.logger.info(f"Successfully retrieved {len(pings)} pings.")
    except Exception as e:
        current_app.logger.error(f"Error getting pings.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error."}), 500
    
    return jsonify([ping.to_dict() for ping in pings]), 200
    

@bot_bp.route('/send_ping', methods=['POST'])
@bot_auth_required
def send_ping():
    ''' Send a ping to a participant '''
    
    # Get request data
    data = request.get_json()
    ping_id = data.get('ping_id')
    
    # Log the start of the request
    current_app.logger.info(f"Received request to send ping={ping_id}.")
    
    # Check if required parameters are present
    if not ping_id:
        current_app.logger.error("Missing ping_id parameter.")
        return jsonify({"error": "Missing ping_id parameter."}), 400
    
    # Get ping
    try:
        ping = Ping.query.get(ping_id)
        if not ping:
            current_app.logger.error(f"Ping {ping_id} not found.")
            return jsonify({"error": "Ping not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting ping {ping_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error."}), 500

    # Send ping
    messenger = TelegramMessenger(
        bot_token=current_app.config['TELEGRAM_BOT_TOKEN'], 
        ping=ping)
    messenger.send_ping()
    
    # Log the end of the request
    current_app.logger.info(f"Successfully sent ping={ping_id}.")
    
    return jsonify({"message": "ping_id={ping.id} sent successfully."}), 200
    
