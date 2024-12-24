from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, PingTemplate, UserStudy
from sqlalchemy.orm import joinedload

ping_templates_bp = Blueprint('ping_templates', __name__)

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

def user_owns_study(user, study_id):
    """
    Helper to check if the user is part of the given study_id.
    """
    study = (
        db.session.query(Study)
        .join(UserStudy)
        .filter(UserStudy.study_id == study_id, UserStudy.user_id == user.id)
        .first()
    )
    if not study:
        current_app.logger.info(f"User {user.id} does not own study {study_id}.")
    return study

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['GET'])
@jwt_required()
def get_ping_templates(study_id=None):
    current_app.logger.info(f"GET request to ping_templates, study_id={study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if study_id:
        current_app.logger.info(f"Fetching ping_templates for user={user.id}, study_id={study_id}")
        study = user_owns_study(user, study_id)

    # Parse query params
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            query = PingTemplate.query.filter_by(study_id=study.id)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        else:
            # fetch all ping templates accessible to user
            query = (
                PingTemplate.query
                .join(Study, Study.id == PingTemplate.study_id)
                .join(UserStudy, UserStudy.study_id == Study.id)
                .filter(UserStudy.user_id == user.id)
            )
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.error("Error querying PingTemplate table.")
        current_app.logger.exception(e)
        return jsonify({"error": "Error retrieving PingTemplates"}), 500

    items = [pt.to_dict() for pt in pagination.items]

    current_app.logger.info(
        f"Returning {len(items)} ping_templates (page {pagination.page}/{pagination.pages}) "
        f"for user={user.id}, study_id={study_id}"
    )

    return jsonify({
        "data": items,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['POST'])
@jwt_required()
def create_ping_template(study_id):
    current_app.logger.info(f"POST request to create ping_template, study_id={study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    data = request.get_json()
    name = data.get('name')
    message = data.get('message')
    url = data.get('url')
    url_text = data.get('url_text')
    reminder_latency = data.get('reminder_latency')
    expire_latency = data.get('expire_latency')
    schedule = data.get('schedule')

    if not name or not message:
        return jsonify({"error": "Missing required fields: name, message"}), 400

    try:
        pt = PingTemplate(
            study_id=study.id,
            name=name,
            message=message,
            url=url,
            url_text=url_text,
            reminder_latency=reminder_latency,
            expire_latency=expire_latency,
            schedule=schedule
        )
        db.session.add(pt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating PingTemplate in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error creating PingTemplate"}), 500

    current_app.logger.info(f"User {user.email} created ping template ID={pt.id} in study={study_id}")

    return jsonify({
        "message": "Ping Template created successfully",
        "ping_template": pt.to_dict()
    }), 201

