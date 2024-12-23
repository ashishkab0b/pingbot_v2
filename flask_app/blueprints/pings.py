from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db
from models import User, Ping, Study, UserStudy

pings_bp = Blueprint('pings', __name__)

def get_current_user():
    """Helper function to get the current user object from the JWT."""
    user_id = get_jwt_identity()
    if not user_id:
        current_app.logger.warning("JWT identity is missing.")
        return None
    user = db.session.get(User, user_id)
    if not user:
        current_app.logger.warning(f"User with id {user_id} not found.")
    return user

def user_has_study_access(user, study_id):
    """
    Helper function to check if the user is part of (has access to) the given study_id.
    Returns the Study object if found; otherwise returns None.
    """
    study = (
        db.session.query(Study)
        .join(UserStudy)
        .filter(UserStudy.study_id == study_id, UserStudy.user_id == user.id)
        .first()
    )
    if not study:
        current_app.logger.info(f"User {user.id} does not have access to study {study_id}.")
    return study

def user_has_ping_access(user, ping_id):
    """
    Helper function to check if the user has access to the ping.
    We'll do this by checking if the ping's study_id is accessible by the user.
    """
    ping = db.session.get(Ping, ping_id)
    if not ping:
        return None

    # Now check if user has access to this ping's study
    study = user_has_study_access(user, ping.study_id)
    if not study:
        return None

    return ping

@pings_bp.route('/pings', methods=['GET'])
@jwt_required()
def get_pings():
    """
    GET /pings
    Optionally supports some filtering (advanced search) via query params.
    For example: ?study_id=1&day_num=2&message=morning
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(f"User {user.email} requested pings with filter {request.args}.")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Optional query params for "advanced search"
    study_id = request.args.get('study_id', type=int)
    day_num = request.args.get('day_num', type=int)
    message = request.args.get('message', type=str)
    enrollment_id = request.args.get('enrollment_id', type=int)

    # Base query: only pings in studies that the user can access
    # We can filter by checking pings that are in a "study" that the user is joined with.
    # A simpler approach is to query all pings, then join to user_study, but that might be more complex.
    # We'll do a sub-query approach: fetch study_ids user can access, then filter by them.
    accessible_study_ids = (
        db.session.query(UserStudy.study_id)
        .filter(UserStudy.user_id == user.id)
        .subquery()
    )

    query = db.session.query(Ping).filter(Ping.study_id.in_(accessible_study_ids))

    # Apply optional filters
    if study_id:
        query = query.filter(Ping.study_id == study_id)
    if day_num is not None:
        query = query.filter(Ping.day_num == day_num)
    if message:
        # Example: partial match on ping message
        query = query.filter(Ping.message.ilike(f"%{message}%"))
    if enrollment_id:
        query = query.filter(Ping.enrollment_id == enrollment_id)

    query = query.order_by(Ping.scheduled_ts.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pings_list = []
    for p in pagination.items:
        pings_list.append({
            "id": p.id,
            "study_id": p.study_id,
            "ping_template_id": p.ping_template_id,
            "enrollment_id": p.enrollment_id,
            "scheduled_ts": p.scheduled_ts.isoformat() if p.scheduled_ts else None,
            "expire_ts": p.expire_ts.isoformat() if p.expire_ts else None,
            "reminder_ts": p.reminder_ts.isoformat() if p.reminder_ts else None,
            "day_num": p.day_num,
            "message": p.message,
            "url": p.url,
            "ping_sent": p.ping_sent,
            "reminder_sent": p.reminder_sent
        })

    return jsonify({
        "data": pings_list,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200

@pings_bp.route('/pings', methods=['POST'])
@jwt_required()
def create_ping():
    """
    POST /pings
    Requires study_id. The user must have access to that study.
    Other fields are optional or required based on your model logic.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    study_id = data.get('study_id')

    # Check user has access to this study
    study = user_has_study_access(user, study_id)
    if not study:
        return jsonify({"error": "No access to study"}), 403

    # Required fields for pings
    enrollment_id = data.get('enrollment_id')
    scheduled_ts = data.get('scheduled_ts')  # e.g. "2024-01-01T09:00:00"
    day_num = data.get('day_num')

    if not all([study_id, enrollment_id, scheduled_ts, day_num]):
        return jsonify({"error": "Missing required fields: study_id, enrollment_id, scheduled_ts, day_num"}), 400

    # Optional
    ping_template_id = data.get('ping_template_id')
    message = data.get('message')
    url = data.get('url')
    expire_ts = data.get('expire_ts')
    reminder_ts = data.get('reminder_ts')

    try:
        new_ping = Ping(
            study_id=study_id,
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
        current_app.logger.error("Error creating ping")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

    current_app.logger.info(f"User {user.email} created a new ping with ID {new_ping.id}.")
    return jsonify({
        "message": "Ping created successfully",
        "ping": {
            "id": new_ping.id,
            "study_id": new_ping.study_id,
            "ping_template_id": new_ping.ping_template_id,
            "enrollment_id": new_ping.enrollment_id,
            "scheduled_ts": new_ping.scheduled_ts.isoformat() if new_ping.scheduled_ts else None,
            "expire_ts": new_ping.expire_ts.isoformat() if new_ping.expire_ts else None,
            "reminder_ts": new_ping.reminder_ts.isoformat() if new_ping.reminder_ts else None,
            "day_num": new_ping.day_num,
            "message": new_ping.message,
            "url": new_ping.url,
            "ping_sent": new_ping.ping_sent,
            "reminder_sent": new_ping.reminder_sent
        }
    }), 201

@pings_bp.route('/pings/<int:ping_id>', methods=['GET'])
@jwt_required()
def get_single_ping(ping_id):
    """
    GET /pings/<ping_id>
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    ping = user_has_ping_access(user, ping_id)
    if not ping:
        return jsonify({"error": "Ping not found or no access"}), 404

    return jsonify({
        "id": ping.id,
        "study_id": ping.study_id,
        "ping_template_id": ping.ping_template_id,
        "enrollment_id": ping.enrollment_id,
        "scheduled_ts": ping.scheduled_ts.isoformat() if ping.scheduled_ts else None,
        "expire_ts": ping.expire_ts.isoformat() if ping.expire_ts else None,
        "reminder_ts": ping.reminder_ts.isoformat() if ping.reminder_ts else None,
        "day_num": ping.day_num,
        "message": ping.message,
        "url": ping.url,
        "ping_sent": ping.ping_sent,
        "reminder_sent": ping.reminder_sent
    }), 200

@pings_bp.route('/pings/<int:ping_id>', methods=['PUT'])
@jwt_required()
def update_ping(ping_id):
    """
    PUT /pings/<ping_id>
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    ping = user_has_ping_access(user, ping_id)
    if not ping:
        return jsonify({"error": "Ping not found or no access"}), 404

    data = request.get_json()

    # Only update fields if they are provided
    if 'ping_template_id' in data:
        ping.ping_template_id = data['ping_template_id']
    if 'enrollment_id' in data:
        ping.enrollment_id = data['enrollment_id']
    if 'scheduled_ts' in data:
        ping.scheduled_ts = data['scheduled_ts']
    if 'expire_ts' in data:
        ping.expire_ts = data['expire_ts']
    if 'reminder_ts' in data:
        ping.reminder_ts = data['reminder_ts']
    if 'day_num' in data:
        ping.day_num = data['day_num']
    if 'message' in data:
        ping.message = data['message']
    if 'url' in data:
        ping.url = data['url']
    if 'ping_sent' in data:
        ping.ping_sent = data['ping_sent']
    if 'reminder_sent' in data:
        ping.reminder_sent = data['reminder_sent']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping {ping_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

    current_app.logger.info(f"User {user.email} updated ping {ping_id}.")
    return jsonify({"message": "Ping updated successfully"}), 200

@pings_bp.route('/pings/<int:ping_id>', methods=['DELETE'])
@jwt_required()
def delete_ping(ping_id):
    """
    DELETE /pings/<ping_id>
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    ping = user_has_ping_access(user, ping_id)
    if not ping:
        return jsonify({"error": "Ping not found or no access"}), 404

    try:
        db.session.delete(ping)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping {ping_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

    current_app.logger.info(f"User {user.email} deleted ping {ping_id}.")
    return jsonify({"message": f"Ping {ping_id} deleted successfully."}), 200