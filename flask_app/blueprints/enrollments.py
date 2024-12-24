from flask import Blueprint, request, g, Response, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import urllib.parse
from random import randint
from datetime import timedelta, datetime, timezone
import pytz
import secrets


from app import db
from utils import generate_non_confusable_code
from permissions import user_has_study_permission, get_current_user
from models import Study, Enrollment, Ping, PingTemplate, User, UserStudy


enrollments_bp = Blueprint('enrollments', __name__)


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

    data = request.get_json()
    # required fields
    tz = data.get('tz')
    study_pid = data.get('study_pid')
    if not all([tz, study_pid]):
        return jsonify({"error": "Missing required fields: tz, study_pid"}), 400

    # optional
    start_date = data.get('start_date', datetime.now(timezone.utc).date())
    enrolled = data.get('enrolled', True)

    try:
        enrollment = Enrollment(
            study_id=study.id,
            tz=tz,
            study_pid=study_pid,
            enrolled=enrolled,
            start_date=start_date
        )
        db.session.add(enrollment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating enrollment in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error creating enrollment"}), 500

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