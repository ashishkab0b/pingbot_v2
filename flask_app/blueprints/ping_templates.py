from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, PingTemplate, UserStudy

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
        current_app.logger.info(f"User {user.id} does not own study {study_id}.")
    return study

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['GET'])
@jwt_required()
def get_ping_templates(study_id):
    """
    Get a paginated list of PingTemplates for a specific study
    that the current user has access to.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = PingTemplate.query.filter_by(study_id=study.id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for pt in pagination.items:
        items.append({
            "id": pt.id,
            "name": pt.name,
            "message": pt.message,
            "url": pt.url,
            "reminder_latency": str(pt.reminder_latency) if pt.reminder_latency else None,
            "expire_latency": str(pt.expire_latency) if pt.expire_latency else None,
            "schedule": pt.schedule  # This is JSON; can directly pass if you want
        })

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
    """
    Create a new PingTemplate under a specific study the current user has access to.
    """
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
    reminder_latency = data.get('reminder_latency')  # e.g. "1 hour"
    expire_latency = data.get('expire_latency')      # e.g. "24 hours"
    schedule = data.get('schedule')                  # JSON object/array
    
    # TODO: Validate the schedule JSON object and other fields
    # 

    if not name or not message:
        return jsonify({"error": "Missing required fields: name, message"}), 400

    try:
        # Construct the PingTemplate
        pt = PingTemplate(
            study_id=study.id,
            name=name,
            message=message,
            url=url,
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

    current_app.logger.info(f"User {user.email} created a ping template ID {pt.id} in study {study_id}.")

    return jsonify({
        "message": "Ping Template created successfully",
        "ping_template": {
            "id": pt.id,
            "name": pt.name,
            "message": pt.message,
            "url": pt.url,
            "reminder_latency": str(pt.reminder_latency) if pt.reminder_latency else None,
            "expire_latency": str(pt.expire_latency) if pt.expire_latency else None,
            "schedule": pt.schedule
        }
    }), 201


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_single_ping_template(study_id, template_id):
    """
    Fetch a single PingTemplate by its ID, under a specific study.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    pt = PingTemplate.query.filter_by(id=template_id, study_id=study.id).first()
    if not pt:
        return jsonify({"error": f"PingTemplate {template_id} not found or no access"}), 404

    return jsonify({
        "id": pt.id,
        "name": pt.name,
        "message": pt.message,
        "url": pt.url,
        "reminder_latency": str(pt.reminder_latency) if pt.reminder_latency else None,
        "expire_latency": str(pt.expire_latency) if pt.expire_latency else None,
        "schedule": pt.schedule
    }), 200


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_ping_template(study_id, template_id):
    """
    Update an existing PingTemplate under a study the user has access to.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    try:
        pt = PingTemplate.query.filter_by(id=template_id, study_id=study.id).first()
        if not pt:
            return jsonify({"error": f"PingTemplate {template_id} not found or no access"}), 404

        data = request.get_json()
        if 'name' in data:
            pt.name = data['name']
        if 'message' in data:
            pt.message = data['message']
        if 'url' in data:
            pt.url = data['url']
        if 'reminder_latency' in data:
            pt.reminder_latency = data['reminder_latency']
        if 'expire_latency' in data:
            pt.expire_latency = data['expire_latency']
        if 'schedule' in data:
            pt.schedule = data['schedule']

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating PingTemplate {template_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error updating PingTemplate"}), 500

    current_app.logger.info(f"User {user.email} updated ping template {template_id} in study {study_id}.")

    return jsonify({
        "message": "Ping Template updated successfully",
        "ping_template": {
            "id": pt.id,
            "name": pt.name,
            "message": pt.message,
            "url": pt.url,
            "reminder_latency": str(pt.reminder_latency) if pt.reminder_latency else None,
            "expire_latency": str(pt.expire_latency) if pt.expire_latency else None,
            "schedule": pt.schedule
        }
    }), 200


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_ping_template(study_id, template_id):
    """
    Delete a PingTemplate from a study the user has access to.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    try:
        pt = PingTemplate.query.filter_by(id=template_id, study_id=study.id).first()
        if not pt:
            return jsonify({"error": f"PingTemplate {template_id} not found or no access"}), 404
        db.session.delete(pt)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting PingTemplate {template_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error deleting PingTemplate"}), 500
    
    current_app.logger.info(f"User {user.email} deleted ping template {template_id} in study {study_id}.")

    return jsonify({"message": f"Ping Template {template_id} deleted successfully."}), 200