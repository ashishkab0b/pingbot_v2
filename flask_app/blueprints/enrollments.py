from flask import Blueprint, request, g, Response, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import CurrentConfig
import urllib.parse
from random import randint
from datetime import timedelta, datetime, timezone
import pytz
import secrets


from app import db
from permissions import user_has_study_permission, get_current_user
from models import Study, Enrollment, Ping, PingTemplate, User, UserStudy


enrollments_bp = Blueprint('enrollments', __name__)


class MessageConstructor:
    """
    This class constructs the message and the URL for a ping.
    Specifically, it replaces variables in the message and URL with values from the database.
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
        
        message = self.ping.ping_template.message
        
        if "<URL>" in self.ping.ping_template.message:
            message = self.ping.ping_template.message.replace("<URL>", self.url)
        
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
    

def random_time(start_date: datetime, start_day_num: int, start_time: str, end_day_num: int, end_time: str, tz: str) -> datetime:
    interval_start_date = start_date + timedelta(days=start_day_num)
    interval_end_date = start_date + timedelta(days=end_day_num)
    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    try:
        tz = pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        current_app.logger.error(f"Invalid timezone {tz}.")
        return
    interval_start_ts = datetime.combine(interval_start_date, start_time, tzinfo=tz)
    interval_end_ts = datetime.combine(interval_end_date, end_time, tzinfo=tz)
    ping_interval_length = interval_end_ts - interval_start_ts
    ping_time = interval_start_ts + timedelta(seconds=randint(0, ping_interval_length.total_seconds()))
    return ping_time
       

def make_pings(enrollment_id, study_id):
    
    current_app.logger.info(f"Making pings for enrollment {enrollment_id} in study {study_id}")
    
    try:
        # Get enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            current_app.logger.error(f"Enrollment {enrollment_id} not found. Aborting ping creation for study {study.id}.")
            return
        
        # Get study
        study = Study.query.get(study_id)
        if not study:
            current_app.logger.error(f"Study {study_id} not found. Aborting ping creation for participant {enrollment_id}.")
            return
        
        # Get ping templates
        ping_templates = study.ping_templates
        if not ping_templates:
            current_app.logger.error(f"No ping templates found for study {study_id}. Aborting ping creation for participant {enrollment_id}.")
            return
        
        # note some assumptions:
        # signup date is Day 0
        # start time and end time are in format HH:MM
        # schedule is a list of dictionaries with keys 'start_day_num', 'start_time', 'end_day_num', 'end_time'
        pings = []
        for pt in ping_templates:
            for ping in pt.schedule:
                # Generate random time within the ping interval
                ping_time = random_time(start_date=enrollment.start_date, 
                                        start_day_num=ping['start_day_num'],
                                        start_time=ping['start_time'],
                                        end_day_num=ping['end_day_num'], 
                                        end_time=ping['end_time'], 
                                        tz=enrollment.tz)
                # Create ping
                ping_data = {
                    'enrollment_id': enrollment_id,
                    'study_id': study_id,
                    'ping_template_id': pt.id,
                    'scheduled_ts': ping_time,
                    'expire_ts': ping_time + pt.expire_latency,
                    'reminder_ts': ping_time + pt.reminder_latency,
                    'day_num': ping['start_day_num'],
                    'message': pt.message,
                    'url': pt.url,
                    'ping_sent': False,
                    'reminder_sent': False 
                }
                ping_obj = Ping(**ping_data)
                db.session.add(ping_obj)
                db.session.flush()
                
                # Construct message and URL
                message_constructor = MessageConstructor(ping_obj)
                url = message_constructor.construct_url()
                message = message_constructor.construct_message()
                ping_obj.url = url
                ping_obj.message = message
                
                # Append to pings list
                pings.append(ping_obj.to_dict())
                
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating pings for enrollment {enrollment_id} in study {study_id}")
        current_app.logger.exception(e)
        return
    
    current_app.logger.info(f"Created {len(pings)} pings for enrollment {enrollment_id} in study {study_id}")
    return pings


    


@enrollments_bp.route('/studies/<int:study_id>/enrollments', methods=['GET'])
@enrollments_bp.route('/enrollments', methods=['GET'])
@jwt_required()
def get_enrollments(study_id=None):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
            if not study:
                return jsonify({"error": f"No access to study {study_id}"}), 403
            query = Enrollment.query.filter_by(study_id=study.id)
        else:
            # fetch all enrollments across studies user can access
            accessible_studies = (
                db.session.query(UserStudy.study_id)
                .filter(UserStudy.user_id == user.id)
                .subquery()
            )
            query = Enrollment.query.filter(Enrollment.study_id.in_(accessible_studies))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [en.to_dict() for en in pagination.items]

        return jsonify({
            "data": items,
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }), 200

    except Exception as e:
        current_app.logger.error("Error retrieving enrollments")
        current_app.logger.exception(e)
        return jsonify({"error": "Error retrieving enrollments"}), 500
    

@enrollments_bp.route('/studies/<int:study_id>/enrollments', methods=['POST'])
@jwt_required()
def create_enrollment(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    # Parse data
    data = request.get_json()
    tz = data.get('tz')
    study_pid = data.get('study_pid')
    telegram_id = data.get('telegram_id', None)  # optional    
    start_date = data.get('start_date', datetime.now(timezone.utc).date())
    enrolled = True if telegram_id else False
    
    # Check if required fields are present
    if not all([tz, study_pid]):
        return jsonify({"error": "Missing required fields: tz, study_pid"}), 400
    
    # Warn if no telegram ID provided
    if not telegram_id:
        current_app.logger.warning("No telegram ID provided for enrollment. Participant will not receive pings.")

    # Make enrollment object and add to database
    try:
        enrollment = Enrollment(
            study_id=study.id,
            tz=tz,
            study_pid=study_pid,
            enrolled=enrolled,
            start_date=start_date,
            telegram_id=telegram_id
        )
        db.session.add(enrollment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating enrollment in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error creating enrollment"}), 500
    
    # Create pings for participant if enrolled (i.e. telegram ID was provided)
    if enrolled and telegram_id:
        pings = make_pings(
            enrollment_id=enrollment.id, 
            study_id=study.id
            )
        if not pings:
            return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "message": "Enrollment created successfully",
        "enrollment": enrollment.to_dict()
    }), 201


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def get_single_enrollment(study_id, enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    enrollment = Enrollment.query.filter_by(id=enrollment_id, study_id=study.id).first()
    if not enrollment:
        return jsonify({"error": f"Enrollment {enrollment_id} not found or no access"}), 404

    return jsonify(enrollment.to_dict()), 200


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def update_enrollment(study_id, enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    enrollment = Enrollment.query.filter_by(id=enrollment_id, study_id=study.id).first()
    if not enrollment:
        return jsonify({"error": f"Enrollment {enrollment_id} not found or no access"}), 404

    data = request.get_json()
    for field in ["telegram_id", "tz", "study_pid", "enrolled", "start_date", "pr_completed"]:
        if field in data:
            setattr(enrollment, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating enrollment {enrollment_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error updating enrollment"}), 500

    return jsonify({
        "message": "Enrollment updated successfully",
        "enrollment": enrollment.to_dict()
    }), 200


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def delete_enrollment(study_id, enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    enrollment = Enrollment.query.filter_by(id=enrollment_id, study_id=study.id).first()
    if not enrollment:
        return jsonify({"error": f"Enrollment {enrollment_id} not found or no access"}), 404

    try:
        db.session.delete(enrollment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting enrollment {enrollment_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error deleting enrollment"}), 500

    return jsonify({"message": f"Enrollment {enrollment_id} deleted successfully."}), 200