from flask import Blueprint, request, jsonify, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Study, PingTemplate, UserStudy, Ping, Enrollment
from permissions import user_has_study_permission, get_current_user
from random import randint
from datetime import timedelta, datetime, timezone
import pytz
from utils import generate_non_confusable_code
import secrets
from blueprints.enrollments import MessageConstructor
from crud import get_enrollments_by_telegram_id, get_study_by_id
from telegram_messenger import TelegramMessenger

particpant_facing_bp = Blueprint('particpant_facing', __name__)


@particpant_facing_bp.route('/ping/<ping_id>', methods=['GET'])
def ping_forwarder(ping_id):
    """
    Forward a ping to the appropriate URL.
    :param ping_id: The ID of the ping to forward.
    
    
    """
    # Log the start of the request
    current_app.logger.info(f"Received request to forward ping, ping_id={ping_id}.")
    
    # Get the ping
    ping = Ping.query.get(ping_id)
    
    # Check if the ping exists
    if not ping:
        current_app.logger.error(f"Failed to find ping with ID {ping_id}.")
        return jsonify({"error": "Ping not found."}), 404
    
    # Get query variable: code
    code = request.args.get('code')
    
    # Check if code is present and matches the ping's code
    if not code or code != ping.forwarding_code:
        current_app.logger.error(f"Invalid forwarding code: {code}.")
        return jsonify({"error": "Invalid code."}), 400
    
    # Update the ping with click timestamps
    try:
        # First clicked timestamp
        if not ping.first_clicked_ts:
            ping.first_clicked_ts = datetime.now(timezone.utc)
            
        # Last clicked timestamp
        ping.last_clicked_ts = datetime.now(timezone.utc)
        
        # Commit changes
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update ping {ping.id} with click timestamps.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error."}), 500
    
    # Check if expired and return message if so
    if ping.expiry_ts and ping.expiry_ts < datetime.now(timezone.utc):
        current_app.logger.info(f"Ping {ping.id} has expired.")
        return current_app.config["PING_EXPIRED_MESSAGE"], 200
    
    # Redirect to survey
    message_constructor = MessageConstructor(ping)
    survey_url = message_constructor.construct_survey_url()
    
    return redirect(survey_url, code=301)


    
@particpant_facing_bp.route('/api/signup', methods=['POST'])
def study_signup():
    '''
    This endpoint is used to collect the timezone of a participant and enroll them in a study.
    It also creates pings for the participant based on the study's ping templates (though this may be moved to after collecting telegram ID).
    They still need to have their telegram ID collected and linked to the enrollment.
    The endpoint ultimately returns a unique code for them (and saves it in the database) that they can provide to the telegram bot 
    in order to link their telegram ID to their enrollment.
    '''
    
    data = request.get_json()
    signup_code = data.get('signup_code')
    study_pid = data.get('study_pid')
    tz = data.get('tz')
    
    # Check if required fields are present
    if not all([signup_code, study_pid, tz]):
        return jsonify({"error": "Missing required fields: signup_code, study_pid, tz"}), 400
    
    # Check if signup code is valid 
    study = Study.query.filter_by(code=signup_code).first()
    if not study:
        return jsonify({"error": "Invalid signup code"}), 404
    
    # Generate a unique code for the participant to link their telegram ID
    telegram_link_code = None
    while True:
        telegram_link_code = generate_non_confusable_code(length=6, lowercase=True, uppercase=False, digits=True)
        if not Enrollment.query.filter_by(telegram_link_code=telegram_link_code).first():
            break
        
    # Create a new enrollment
    try:
        utc_now = datetime.now(timezone.utc)
        enrollment = Enrollment(study_id=study.id, 
                                tz=tz,
                                enrolled=False,  # This will be set to True once the telegram ID is linked
                                study_pid=study_pid,
                                signup_ts=utc_now,
                                pr_completed=0.0,
                                telegram_link_code=telegram_link_code,
                                telegram_link_code_expire_ts=utc_now + timedelta(days=current_app.config["TELEGRAM_LINK_CODE_EXPIRY_DAYS"])
                                )
        db.session.add(enrollment)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error with enrollment in study={study.id} using signup code={signup_code} for study_pid={study_pid}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500
    

    
    return jsonify({
        "message": "Participant enrolled successfully",
        "telegram_link_code": telegram_link_code,
        "participant_id": enrollment.id,
        "study_id": study.id,
        "study_pid": study_pid,
        "tz": enrollment.tz
    }), 200


@particpant_facing_bp.route('/api/participant_dashboard', methods=['GET'])
def api_participant_dashboard():
    '''
    This endpoint is used to provide data to render the participant dashboard.
    '''
    
    current_app.logger.debug("Entered participant_dashboard endpoint.")
    study_keys_to_return = ['public_name', 'contact_message']
    enrollment_keys_to_return = ['study_pid', 'tz', 'study_id', 'enrolled', 'signup_ts']
    
    telegram_id = request.args.get('t')
    otp = request.args.get('otp')
    
    # Check if OTP is valid and get the enrollment objects
    enrollments = get_enrollments_by_telegram_id(db.session, telegram_id)
    if not enrollments:
        current_app.logger.error(f"Participant not found for telegram_id={telegram_id} with OTP={otp}")
        return jsonify({"error": "Participant not found"}), 404
    valid_enrollments = []
    for enrollment in enrollments:
        if enrollment.dashboard_otp == otp and enrollment.dashboard_otp_expire_ts > datetime.now(timezone.utc):
            en = {k: v for k,v in enrollment.to_dict().items() if k in enrollment_keys_to_return}
            study = get_study_by_id(db.session, enrollment.study_id).to_dict()
            for k,v in study.items():
                if k in study_keys_to_return:
                    en[k] = v
            signup_date = datetime.fromisoformat(en['signup_ts'])
            signup_date = signup_date.astimezone(pytz.timezone(en['tz']))
            en['signup_ts'] = signup_date.strftime("%Y-%m-%d")
            valid_enrollments.append(en)
            
    if not valid_enrollments:
        return jsonify({"error": "Invalid OTP"}), 400
    
    return jsonify(valid_enrollments), 200


    
    
    
    