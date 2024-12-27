from flask import Blueprint, request, jsonify, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, PingTemplate, UserStudy, Ping, Enrollment
from permissions import user_has_study_permission, get_current_user
from random import randint
from datetime import timedelta, datetime, timezone
import pytz
from utils import generate_non_confusable_code
import secrets

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
    
    # Redirect to ping.url
    return redirect(ping.url)


    
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
        enrollment = Enrollment(study_id=study.id, 
                                tz=tz,
                                enrolled=True, 
                                study_pid=study_pid,
                                start_date=datetime.now().date(),
                                pr_completed=0.0,
                                telegram_link_code=telegram_link_code,
                                telegram_link_code_expire_ts=datetime.now(timezone.utc) + timedelta(days=current_app.config["TELEGRAM_LINK_CODE_EXPIRY_DAYS"])
                                )
        db.session.add(enrollment)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error with enrollment in study {study.id} using signup code {signup_code} for study pid {study_pid}")
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
    


@particpant_facing_bp.route('/enrollment/login', methods=['POST'])
def participant_login():
    '''
    This endpoint is used to generate a one-time login link for a participant.
    '''
    
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    
    # Create a new OTP
    otp = secrets.token_urlsafe(16)
    otp_lifespan = current_app.config["ENROLLMENT_DASHBOARD_OTP_EXPIRY_MINS"]
    expiry = datetime.now() + timedelta(minutes=otp_lifespan)
    
    # Save the OTP
    try:
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.dashboard_otp = otp
        user.dashboard_otp_expire_ts = expiry
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating OTP for user {telegram_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500
    
    # Send the OTP to the user
    
    

    
    
    
    