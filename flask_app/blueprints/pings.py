from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db
from models import User, Ping, Study, UserStudy, Enrollment
from permissions import user_has_study_permission, get_current_user
from datetime import datetime
from pytz import UTC, timezone

pings_bp = Blueprint('pings', __name__)


def convert_utc_to_local(utc_datetime, participant_tz):
    """
    Convert a UTC datetime object to the participant's local time zone.
    Returns an ISO8601 string or None if invalid.
    """
    if not utc_datetime or not participant_tz:
        return None
    try:
        # Ensure the scheduled_ts is considered UTC
        utc_dt = utc_datetime.replace(tzinfo=UTC)
        local_tz = timezone(participant_tz)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.isoformat()
    except Exception as e:
        current_app.logger.warning(f"Error converting time with tz={participant_tz}: {e}")
        return None
    
def prepare_requested_ping(ping: Ping) -> dict:
    """
    Prepare a ping for response.
    """
    ping_dict = ping.to_dict()
    
    # Fetch the participant's Enrollment for the time zone
    enrollment = db.session.get(Enrollment, ping.enrollment_id)
    if enrollment:
        participant_tz = enrollment.tz
        # Convert UTC datetime to participant's local time
        local_ts = convert_utc_to_local(ping.scheduled_ts, participant_tz)
        ping_dict['scheduled_ts_local'] = local_ts
    return ping_dict

@pings_bp.route('/studies/<int:study_id>/pings', methods=['GET'])
@pings_bp.route('/pings', methods=['GET'])
@jwt_required()
def get_pings(study_id=None):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    else:
        current_app.logger.info(f"User {user.email} requested pings for study {study_id}.")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            # Verify access
            study = user_has_study_permission(
                user_id=user.id,
                study_id=study_id,
                minimum_role="viewer"
            )
            if not study:
                return jsonify({"error": f"No access to study {study_id}"}), 403

            query = Ping.query.filter_by(study_id=study.id)
        else:
            # all pings across all studies the user can access
            accessible_studies = (
                db.session.query(UserStudy.study_id)
                .filter(UserStudy.user_id == user.id)
                .subquery()
            )
            query = Ping.query.filter(Ping.study_id.in_(accessible_studies))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for p in pagination.items:
            p_dict = prepare_requested_ping(p)
            items.append(p_dict)

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
        current_app.logger.error("Error retrieving pings")
        current_app.logger.exception(e)
        return jsonify({"error": "Error retrieving pings"}), 500


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['GET'])
@jwt_required()
def get_single_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404
    
    p_dict = prepare_requested_ping(p)
    
    return jsonify(p_dict), 200

@pings_bp.route('/studies/<int:study_id>/pings', methods=['POST'])
@jwt_required()
def create_ping(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    data = request.get_json()
    # minimal required fields
    enrollment_id = data.get('enrollment_id')
    scheduled_ts = data.get('scheduled_ts')
    day_num = data.get('day_num')

    if not all([enrollment_id, scheduled_ts, day_num]):
        return jsonify({"error": "Missing required fields: enrollment_id, scheduled_ts, day_num"}), 400

    # optional
    ping_template_id = data.get('ping_template_id')
    message = data.get('message')
    url = data.get('url')
    expire_ts = data.get('expire_ts')
    reminder_ts = data.get('reminder_ts')

    try:
        new_ping = Ping(
            study_id=study.id,
            ping_template_id=ping_template_id,
            enrollment_id=enrollment_id,
            scheduled_ts=scheduled_ts,
            expire_ts=expire_ts,
            reminder_ts=reminder_ts,
            day_num=day_num,
            message=message,
            url=url
        )
        db.session.add(new_ping)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating ping in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error creating ping"}), 500

    return jsonify({
        "message": "Ping created successfully",
        "ping": new_ping.to_dict()
    }), 201

@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['PUT'])
@jwt_required()
def update_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404

    data = request.get_json()
    # update any provided fields
    for field in ["ping_template_id", "enrollment_id", "scheduled_ts", "expire_ts",
                  "reminder_ts", "day_num", "message", "url", "ping_sent", "reminder_sent"]:
        if field in data:
            setattr(p, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping {ping_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error updating ping"}), 500

    return jsonify({"message": "Ping updated", "ping": p.to_dict()}), 200


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['DELETE'])
@jwt_required()
def delete_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404

    try:
        db.session.delete(p)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping {ping_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error deleting ping"}), 500

    return jsonify({"message": f"Ping {ping_id} deleted successfully."}), 200