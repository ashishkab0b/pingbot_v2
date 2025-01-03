
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone

from extensions import db
from crud import (
    get_study_by_id,
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
from sqlalchemy import select
    


def make_pings(enrollment_id, study_id):
    current_app.logger.info(f"Making pings for enrollment={enrollment_id} in study={study_id}")
    
    try:
        # Get enrollment
        enrollment = get_enrollment_by_id(db.session, enrollment_id)
        if not enrollment:
            current_app.logger.error(
                f"Enrollment={enrollment_id} not found. Aborting ping creation for study={study_id}."
            )
            return
        
        # Get study
        study = get_study_by_id(db.session, study_id)
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
                    signup_ts=enrollment.signup_ts, 
                    begin_day_num=ping_obj['begin_day_num'],
                    begin_time=ping_obj['begin_time'],
                    end_day_num=ping_obj['end_day_num'], 
                    end_time=ping_obj['end_time'], 
                    tz=enrollment.tz
                )
                # current_app.logger.debug(f"Generated ping with scheduled time: {ping_time}")
            
                expire_ts = ping_time + pt.expire_latency if pt.expire_latency else None
                reminder_ts = ping_time + pt.reminder_latency if pt.reminder_latency else None        
                
                new_ping_data = {
                    'enrollment_id': enrollment_id,
                    'study_id': study_id,
                    'ping_template_id': pt.id,
                    'scheduled_ts': ping_time,
                    'expire_ts': expire_ts,
                    'reminder_ts': reminder_ts,
                    'day_num': ping_obj['begin_day_num']
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
    """
    Get a list of enrollments for a given study, with pagination, sorting, and searching.

    Args:
        study_id (int): The ID of the study.

    Query Parameters:
        page (int): The page number (default: 1).
        per_page (int): The number of items per page (default: 10).
        sort_by (str): The field to sort by (default: 'id').
        sort_order (str): The sort order, 'asc' or 'desc' (default: 'asc').
        search (str): A search query to filter enrollments by study_pid.

    Returns:
        JSON response containing the list of enrollments and pagination metadata.
    """
    current_app.logger.debug("Entered get_enrollments route.")

    user = get_current_user()
    if not user:
        current_app.logger.warning("Attempted to fetch enrollments but user not found.")
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(f"User={user.email} requested enrollments for study={study_id}.")

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
            current_app.logger.warning(f"User={user.id} does not have access to study={study_id}.")
            return jsonify({"error": f"Study={study_id} not found or no access"}), 403

        # Build base query
        stmt = select(Enrollment).where(
            Enrollment.study_id == study_id,
            Enrollment.deleted_at.is_(None)
        )

        # Apply search filter
        if search_query:
            stmt = stmt.where(Enrollment.study_pid.ilike(f'%{search_query}%'))

        # Apply sorting
        valid_sort_columns = {
            'id': Enrollment.id,
            'study_pid': Enrollment.study_pid,
            'signup_ts': Enrollment.signup_ts,
            'tz': Enrollment.tz,
            'enrolled': Enrollment.enrolled,
            'pr_completed': Enrollment.pr_completed,
            'linked_telegram': Enrollment.telegram_id.isnot(None),
            'signup_ts': Enrollment.signup_ts
            
        }
        sort_column = valid_sort_columns.get(sort_by, Enrollment.id)

        if sort_order.lower() == 'desc':
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Paginate
        pagination = paginate_statement(db.session, stmt, page=page, per_page=per_page)
        items = []
        for en in pagination['items']:
            item = {
                "id": en.id,
                "tz": en.tz,
                "study_pid": en.study_pid,
                "linked_telegram": en.telegram_id is not None,
                "enrolled": en.enrolled,
                "signup_ts": convert_dt_to_local(en.signup_ts, en.tz).strftime("%Y-%m-%d"),
                "pr_completed": en.pr_completed,
            }
            items.append(item)

        current_app.logger.info(
            f"User={user.email} fetched {len(items)} enrollments on page {pagination['page']}/{pagination['pages']}."
        )

        return jsonify({
            "data": items,
            "meta": {
                "page": pagination['page'],
                "per_page": pagination['per_page'],
                "total": pagination['total'],
                "pages": pagination['pages']
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching enrollments for study={study_id}: {e}")
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