from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from pytz import UTC, timezone

from extensions import db
from crud import (
    get_ping_by_id,
    create_ping,
    update_ping,
    soft_delete_ping,
    get_enrollment_by_id,
)
from permissions import get_current_user, user_has_study_permission
from utils import paginate_statement
from models import Ping

pings_bp = Blueprint('pings', __name__)


def convert_utc_to_local(utc_datetime, participant_tz):
    """
    Convert a UTC datetime object to the participant's local time zone.
    Returns an ISO8601 string or None if invalid.
    """
    if not utc_datetime or not participant_tz:
        return None
    try:
        utc_dt = utc_datetime.replace(tzinfo=UTC)
        local_tz = timezone(participant_tz)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.isoformat()
    except Exception as e:
        current_app.logger.warning(f"Error converting time with tz={participant_tz}: {e}")
        return None


def prepare_requested_ping(ping):
    """
    Prepare a ping for response.
    """
    ping_dict = ping.to_dict()

    enrollment = get_enrollment_by_id(db.session, ping.enrollment_id)
    if enrollment:
        participant_tz = enrollment.tz
        local_ts = convert_utc_to_local(ping.scheduled_ts, participant_tz)
        ping_dict['scheduled_ts_local'] = local_ts
    return ping_dict


@pings_bp.route('/studies/<int:study_id>/pings', methods=['GET'])
@jwt_required()
def get_pings(study_id=None):
    current_app.logger.debug(f"Entered get_pings route for study {study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while fetching pings.")
        return jsonify({"error": "User not found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
            if not study:
                current_app.logger.warning(
                    f"User={user.email} does not have access to study {study_id}."
                )
                return jsonify({"error": f"No access to study {study_id}"}), 403

            query = db.session.query(Ping).filter_by(study_id=study.id, deleted_at=None)
        else:
            current_app.logger.error("Pings across all studies are not supported in this route.")
            return jsonify({"error": "Study ID is required"}), 400

        pagination = paginate_statement(db.session, query.statement, page=page, per_page=per_page)

        items = [prepare_requested_ping(p) for p in pagination["items"]]

        current_app.logger.info(f"User={user.email} fetched {len(items)} pings for study {study_id}.")
        return jsonify({
            "data": items,
            "meta": {
                "page": pagination["page"],
                "per_page": pagination["per_page"],
                "total": pagination["total"],
                "pages": pagination["pages"]
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching pings for study {study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@pings_bp.route('/studies/<int:study_id>/pings', methods=['POST'])
@jwt_required()
def create_ping_route(study_id):
    current_app.logger.debug(f"Entered create_ping route for study {study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while creating a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to create pings in study {study_id}."
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
    current_app.logger.debug(f"Entered update_ping route for ping {ping_id} in study {study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while updating a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to update pings in study {study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    ping = get_ping_by_id(db.session, ping_id)
    if not ping or ping.deleted_at is not None:
        current_app.logger.warning(f"Ping {ping_id} not found or is deleted.")
        return jsonify({"error": "Ping not found or no access"}), 404

    data = request.get_json()
    try:
        updated_ping = update_ping(db.session, ping_id, **data)
        db.session.commit()
        current_app.logger.info(f"User={user.email} updated ping {ping_id} in study {study_id}.")
        return jsonify({"message": "Ping updated successfully", "ping": updated_ping.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping {ping_id} in study {study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['DELETE'])
@jwt_required()
def delete_ping_route(study_id, ping_id):
    current_app.logger.debug(f"Entered delete_ping route for ping {ping_id} in study {study_id}.")
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while deleting a ping.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} does not have access to delete pings in study {study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    ping = get_ping_by_id(db.session, ping_id)
    if not ping or ping.deleted_at is not None:
        current_app.logger.warning(f"Ping {ping_id} not found or is already deleted.")
        return jsonify({"error": "Ping not found or no access"}), 404

    try:
        if not soft_delete_ping(db.session, ping_id):
            current_app.logger.warning(f"Soft delete failed for ping {ping_id}.")
            return jsonify({"error": "Could not delete ping"}), 404
        db.session.commit()
        current_app.logger.info(f"User={user.email} soft deleted ping {ping_id} in study {study_id}.")
        return jsonify({"message": f"Ping {ping_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping {ping_id} in study {study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500