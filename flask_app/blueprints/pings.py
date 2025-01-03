from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import select

from extensions import db
from crud import (
    get_ping_by_id,
    create_ping,
    update_ping,
    soft_delete_ping,
    get_enrollment_by_id,
)
from permissions import get_current_user, user_has_study_permission
from utils import convert_dt_to_local, paginate_statement
from models import Ping, PingTemplate, Enrollment

pings_bp = Blueprint('pings', __name__)


def prepare_requested_ping(ping):
    """
    Prepare a ping for response by adding information from enrollment
    """
    ping_dict = ping.to_dict()

    enrollment = get_enrollment_by_id(db.session, ping.enrollment_id)

    if enrollment:
        # Add the participant's time zone
        participant_tz = enrollment.tz
        local_ts = convert_dt_to_local(ping.scheduled_ts, participant_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        ping_dict['scheduled_ts_local'] = local_ts
        if ping_dict['first_clicked_ts']:
            ping_dict['first_clicked_ts'] = convert_dt_to_local(ping.first_clicked_ts, participant_tz).strftime("%Y-%m-%d %H:%M:%S %Z")

        # Add study pid
        ping_dict['pid'] = enrollment.study_pid

    # Handle possible NoneType for ping_template
    if ping.ping_template:
        ping_dict['ping_template_name'] = ping.ping_template.name
    else:
        ping_dict['ping_template_name'] = None

    return ping_dict

@pings_bp.route('/studies/<int:study_id>/pings', methods=['GET'])
@jwt_required()
def get_pings(study_id):
    current_app.logger.debug(f"Entered get_pings route for study={study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while fetching pings.")
        return jsonify({"error": "User not found"}), 404

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Get search query
    search_query = request.args.get('search', None)

    try:
        # Validate user permissions
        study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
        if not study:
            return jsonify({"error": f"No access to study {study_id}"}), 403

        # Build base query with join
        stmt = (select(Ping)
                .join(Enrollment, Ping.enrollment_id == Enrollment.id)
                .join(PingTemplate, Ping.ping_template_id == PingTemplate.id)
                .where(
                    Ping.study_id == study.id,
                    Ping.deleted_at.is_(None)
                ))

        # Apply search filter
        if search_query:
            stmt = stmt.where(Enrollment.study_pid.ilike(f'%{search_query}%'))

        # Apply sorting
        valid_sort_columns = {
            'id': Ping.id,
            'scheduled': Ping.scheduled_ts,
            'dayNum': Ping.day_num,
            'participantId': Enrollment.study_pid,
            'pingTemplate': PingTemplate.name,
        }
        sort_column = valid_sort_columns.get(sort_by, Ping.id)

        if sort_order.lower() == 'desc':
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Paginate
        pagination = paginate_statement(session=db.session, stmt=stmt, page=page, per_page=per_page)
        items = [prepare_requested_ping(ping) for ping in pagination['items']]

        return jsonify({
            "data": items,
            "meta": {
                "page": pagination['page'],
                "per_page": pagination['per_page'],
                "total": pagination['total'],
                "pages": pagination['pages'],
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching pings for study={study_id}: {e}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@pings_bp.route('/studies/<int:study_id>/pings', methods=['POST'])
@jwt_required()
def create_ping_route(study_id):
    current_app.logger.debug(f"Entered create_ping route for study={study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while creating a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to create pings in study={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    data = request.get_json()
    required_fields = ['enrollment_id', 'scheduled_ts', 'day_num']
    if not all(field in data for field in required_fields):
        current_app.logger.error(f"Missing required fields for ping creation: {data}")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_ping = create_ping(db.session, study_id=study.id, **data)
        db.session.commit()
        current_app.logger.info(f"User={user.email} created a new ping in study {study_id}.")
        return jsonify({"message": "Ping created successfully", "ping": new_ping.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating ping in study {study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['PUT'])
@jwt_required()
def update_ping_route(study_id, ping_id):
    current_app.logger.debug(f"Entered update_ping route for ping={ping_id} in study={study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while updating a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to update pings in study={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    ping = get_ping_by_id(db.session, ping_id)
    if not ping or ping.deleted_at is not None:
        current_app.logger.warning(f"Ping={ping_id} not found or is deleted.")
        return jsonify({"error": "Ping not found or no access"}), 404

    data = request.get_json()
    try:
        updated_ping = update_ping(db.session, ping_id, **data)
        db.session.commit()
        current_app.logger.info(f"User={user.email} updated ping={ping_id} in study={study_id}.")
        return jsonify({"message": "Ping updated successfully", "ping": updated_ping.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping={ping_id} in study={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['DELETE'])
@jwt_required()
def delete_ping_route(study_id, ping_id):
    current_app.logger.debug(f"Entered delete_ping route for ping={ping_id} in study={study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while deleting a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to delete pings in study={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    ping = get_ping_by_id(db.session, ping_id)
    if not ping or ping.deleted_at is not None:
        current_app.logger.warning(f"Ping={ping_id} not found or is already deleted.")
        return jsonify({"error": "Ping not found or no access"}), 404

    try:
        if not soft_delete_ping(db.session, ping_id):
            current_app.logger.warning(f"Soft delete failed for ping={ping_id}.")
            return jsonify({"error": "Could not delete ping"}), 404
        db.session.commit()
        current_app.logger.info(f"User={user.email} soft deleted ping={ping_id} in study={study_id}.")
        return jsonify({"message": f"Ping {ping_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping={ping_id} in study={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500