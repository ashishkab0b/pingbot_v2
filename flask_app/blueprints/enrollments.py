
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone

from extensions import db
from crud import (
    create_enrollment,
    get_enrollment_by_id,
    update_enrollment,
    soft_delete_enrollment,
    get_user_study_relation,
    soft_delete_all_pings_for_enrollment
)
from permissions import get_current_user, user_has_study_permission
from utils import paginate_statement, random_time, convert_dt_to_local

from models import Enrollment, Study, Ping




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
        "<ENROLLMENT_SIGNUP_DATE>": {
            "description": "The date the participant enrolled in the study.",
            "db_table": "enrollments",
            "db_column": "signup_ts_local",
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
        Initialize with the provided ping.
        """
        self.ping = ping
        self.telegram_id = self.ping.enrollment.telegram_id
        self.url = None
        self.survey_link = None
        self.message = None
        
    def construct_ping_link(self):
        """
        Construct an HTML link for the ping. 
        This is done at the point of sending the ping.
        """
        forwarding_code = self.ping.forwarding_code
        url = f"{current_app.config['PING_LINK_BASE_URL']}/ping/{self.ping.id}?code={forwarding_code}"
        url_text = self.ping.ping_template.url_text if self.ping.ping_template.url_text else current_app.config['PING_DEFAULT_URL_TEXT']
        self.survey_link = f"<a href='{url}'>{url_text}</a>"
        
        return self.survey_link
        
    def construct_message(self):
        """
        Construct a message with a URL.
        This is done at the point of sending the ping.
        """
        message = self.ping.ping_template.message
        survey_link = self.construct_ping_link() if self.ping.ping_template.url else None
        
        if "<URL>" in self.ping.ping_template.message:
            message = message.replace("<URL>", survey_link)
        elif survey_link:
            message += f"\n\n{survey_link}"
        
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
        
    def construct_survey_url(self):
        """
        Construct a URL for a ping. 
        This is done in the ping forwarding route at the point of redirecting to the survey after the participant clicks.
        """
        url = self.ping.ping_template.url

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
    


def make_pings(enrollment_id, study_id):
    current_app.logger.info(f"Making pings for enrollment={enrollment_id} in study={study_id}")
    
    try:
        # Get enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            current_app.logger.error(
                f"Enrollment={enrollment_id} not found. Aborting ping creation for study={study_id}."
            )
            return
        
        # Get study
        study = Study.query.get(study_id)
        if not study:
            current_app.logger.error(
                f"Study={study_id} not found. Aborting ping creation for enrollment={enrollment_id}."
            )
            return
        
        # Get ping templates
        ping_templates = study.ping_templates
        if not ping_templates:
            current_app.logger.error(
                f"No ping templates found for study={study_id}. Aborting ping creation for enrollment={enrollment_id}."
            )
            return
        
        pings = []
        for pt in ping_templates:
            for ping_obj in pt.schedule:
                # Generate random time within the ping interval
                ping_time = random_time(
                    start_date=enrollment.signup_ts_local, 
                    begin_day_num=ping_obj['begin_day_num'],
                    begin_time=ping_obj['begin_time'],
                    end_day_num=ping_obj['end_day_num'], 
                    end_time=ping_obj['end_time'], 
                    tz=enrollment.tz
                )
            
                expire_ts = ping_time + pt.expire_latency if pt.expire_latency else None
                reminder_ts = ping_time + pt.reminder_latency if pt.reminder_latency else None        
                
                new_ping_data = {
                    'enrollment_id': enrollment_id,
                    'study_id': study_id,
                    'ping_template_id': pt.id,
                    'scheduled_ts': ping_time,
                    'expire_ts': expire_ts,
                    'reminder_ts': reminder_ts,
                    'day_num': ping_obj['begin_day_num'],
                    'ping_sent': False,
                    'reminder_sent': False 
                }
                ping_instance = Ping(**new_ping_data)
                db.session.add(ping_instance)
                
                # Keep track of the new ping in a list (for returning).
                pings.append(ping_instance.to_dict())
                
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error creating pings for enrollment={enrollment_id} in study={study_id}"
        )
        current_app.logger.exception(e)
        return
    
    current_app.logger.info(
        f"Created {len(pings)} pings for enrollment={enrollment_id} in study={study_id}"
    )
    return pings

enrollments_bp = Blueprint('enrollments', __name__)


@enrollments_bp.route('/studies/<int:study_id>/enrollments', methods=['GET'])
@jwt_required()
def get_enrollments(study_id):
    current_app.logger.debug("Entered get_enrollments route.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("Attempted to fetch enrollments but user not found.")
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(f"User={user.email} requested enrollments for study={study_id}.")
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(f"User={user.id} does not have access to study={study_id}.")
        return jsonify({"error": f"Study={study_id} not found or no access"}), 403

    stmt = (
        db.session.query(Enrollment)
        .filter_by(study_id=study_id)
        .filter(Enrollment.deleted_at.is_(None))
        .order_by(Enrollment.id.asc())
        .statement
    )

    pagination = paginate_statement(db.session, stmt, page=page, per_page=per_page)

    enrollments_list = [
        {
            "id": en.id,
            "tz": en.tz,
            "study_pid": en.study_pid,
            "telegram_id": en.telegram_id,
            "enrolled": en.enrolled,
            "signup_ts_local": convert_dt_to_local(en.signup_ts_local, en.tz).strftime("%Y-%m-%d"),
        }
        for en in pagination["items"]
    ]

    current_app.logger.info(
        f"User={user.email} fetched {len(enrollments_list)} enrollments on page {page}/{pagination['pages']}."
    )

    return jsonify({
        "data": enrollments_list,
        "meta": {
            "page": pagination["page"],
            "per_page": pagination["per_page"],
            "total": pagination["total"],
            "pages": pagination["pages"]
        }
    }), 200


@enrollments_bp.route('/studies/<int:study_id>/enrollments', methods=['POST'])
@jwt_required()
def create_enrollment_route(study_id):
    current_app.logger.debug("Entered create_enrollment route.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while trying to create an enrollment.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(f"User={user.id} does not have editor access to study={study_id}.")
        return jsonify({"error": f"Study={study_id} not found or no access"}), 403

    data = request.get_json()
    tz = data.get('tz')
    study_pid = data.get('study_pid')
    telegram_id = data.get('telegram_id', None)
    signup_ts_local = data.get('signup_ts_local', datetime.now(timezone.utc))
    enrolled = bool(telegram_id)

    if not all([tz, study_pid]):
        current_app.logger.warning(f"Missing required fields in create_enrollment with data={data}.")
        return jsonify({"error": "Missing required fields: tz, study_pid"}), 400

    try:
        new_enrollment = create_enrollment(
            db.session,
            study_id=study_id,
            tz=tz,
            study_pid=study_pid,
            enrolled=enrolled,
            signup_ts_local=signup_ts_local,
            telegram_id=telegram_id
        )
        db.session.commit()

        current_app.logger.info(f"User={user.email} created a new enrollment={new_enrollment.id} in study={study_id}.")
        return jsonify({
            "message": "Enrollment created successfully",
            "enrollment": {
                "id": new_enrollment.id,
                "tz": new_enrollment.tz,
                "study_pid": new_enrollment.study_pid,
                "telegram_id": new_enrollment.telegram_id,
                "enrolled": new_enrollment.enrolled,
                "signup_ts_local": new_enrollment.signup_ts_local
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating enrollment in study={study_id} with data={data}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def get_single_enrollment_route(study_id, enrollment_id):
    current_app.logger.debug(f"Entered get_single_enrollment route for enrollment {enrollment_id}.")

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while accessing an enrollment.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(
            f"User={user.id} attempted to access enrollment={enrollment_id} without permissions."
        )
        return jsonify({"error": f"Study {study_id} not found or no access"}), 403

    enrollment = get_enrollment_by_id(db.session, enrollment_id)
    if not enrollment:
        current_app.logger.warning(
            f"User={user.id} attempted to access nonexistent enrollment={enrollment_id}."
        )
        return jsonify({"error": "Enrollment not found"}), 404

    current_app.logger.info(f"User={user.email} accessed enrollment={enrollment_id}.")
    return jsonify(enrollment.to_dict()), 200


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def update_enrollment_route(study_id, enrollment_id):
    current_app.logger.debug(f"Entered update_enrollment route for enrollment={enrollment_id}.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while trying to update an enrollment.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.id} attempted to update enrollment={enrollment_id} without permissions."
        )
        return jsonify({"error": f"Study {study_id} not found or no access"}), 403

    data = request.get_json()
    try:
        updated_enrollment = update_enrollment(db.session, enrollment_id, **data)
        db.session.commit()

        current_app.logger.info(f"User={user.email} updated enrollment={enrollment_id}.")
        return jsonify({
            "message": "Enrollment updated successfully",
            "enrollment": updated_enrollment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating enrollment={enrollment_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@enrollments_bp.route('/studies/<int:study_id>/enrollments/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def delete_enrollment_route(study_id, enrollment_id):
    current_app.logger.debug(f"Entered delete_enrollment route for enrollment={enrollment_id}.")

    # Get the current user
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while trying to delete an enrollment.")
        return jsonify({"error": "User not found"}), 404

    # Check if the user has permission to delete the enrollment
    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.id} attempted to delete enrollment={enrollment_id} without permissions."
        )
        return jsonify({"error": f"Study {study_id} not found or no access"}), 403

    try:
        # Attempt to soft-delete the enrollment
        if not soft_delete_enrollment(db.session, enrollment_id):
            current_app.logger.warning(
                f"Failed to soft-delete enrollment={enrollment_id}. Possibly nonexistent."
            )
            return jsonify({"error": "Enrollment not found"}), 404
        
        # Attempt to soft-delete the pings
        if not soft_delete_all_pings_for_enrollment(db.session, enrollment_id):
            current_app.logger.warning(
                f"Failed to soft-delete pings for enrollment={enrollment_id}."
            )
            return jsonify({"error": "Internal server error"}), 500
        

        db.session.commit()

        current_app.logger.info(f"User={user.email} deleted enrollment={enrollment_id}.")
        return jsonify({"message": f"Enrollment {enrollment_id} deleted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting enrollment={enrollment_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500