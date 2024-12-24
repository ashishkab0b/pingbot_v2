"""
ping_templates.py

Blueprint for creating, retrieving, updating, and deleting PingTemplate objects.
Includes both "global" style (all ping templates user can access) and
"study-specific" routes (under /studies/<study_id>/ping_templates).

Routes:
    - GET /studies/<int:study_id>/ping_templates
    - GET /ping_templates (optional "global" listing)
    - POST /studies/<int:study_id>/ping_templates
    - GET /studies/<int:study_id>/ping_templates/<int:template_id>
    - PUT /studies/<int:study_id>/ping_templates/<int:template_id>
    - DELETE /studies/<int:study_id>/ping_templates/<int:template_id>
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app import db
from models import Study, PingTemplate, UserStudy
from permissions import get_current_user, user_has_study_permission
from sqlalchemy.orm import joinedload
from typing import Any, Optional

ping_templates_bp = Blueprint('ping_templates', __name__)


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['GET'])
@ping_templates_bp.route('/ping_templates', methods=['GET'])
@jwt_required()
def get_ping_templates(study_id: Optional[int] = None) -> Any:
    """
    Retrieve a paginated list of PingTemplates. If study_id is provided, list PingTemplates
    under that study (if the user has at least 'viewer' role). Otherwise, list all templates 
    in studies the user can access.

    ---
    parameters:
      - name: study_id
        in: path
        type: integer
        required: false
        description: The ID of the study.
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination (default: 1).
      - name: per_page
        in: query
        type: integer
        required: false
        description: Number of items per page (default: 10).
    responses:
      200:
        description: Paginated list of PingTemplates.
      403:
        description: Access denied to the study.
      404:
        description: User not found.
      500:
        description: Server error retrieving PingTemplates.
    """
    current_app.logger.info(f"GET request to ping_templates, study_id={study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if study_id:
        current_app.logger.info(f"Fetching ping_templates for user={user.id}, study_id={study_id}")
        study = user_has_study_permission(user.id, study_id, minimum_role="viewer")
        if not study:
            current_app.logger.warning(f"User {user.id} lacks permission to study {study_id}.")
            return jsonify({"error": f"No access to study {study_id}"}), 403

    # Parse pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            query = PingTemplate.query.filter_by(study_id=study_id)
        else:
            accessible_studies = (
                db.session.query(UserStudy.study_id)
                .filter(UserStudy.user_id == user.id)
                .subquery()
            )
            query = PingTemplate.query.filter(PingTemplate.study_id.in_(accessible_studies))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
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

    except Exception as e:
        current_app.logger.error("Error querying PingTemplate table.")
        current_app.logger.exception(e)
        return jsonify({"error": "Error retrieving PingTemplates"}), 500

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['POST'])
@jwt_required()
def create_ping_template(study_id: int) -> Any:
    """
    Create a new PingTemplate under the given study. Requires 'editor' role or higher.

    ---
    parameters:
      - name: study_id
        in: path
        type: integer
        required: true
        description: The ID of the study.
    requestBody:
      description: JSON payload with the details of the new PingTemplate.
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: Name of the PingTemplate.
              message:
                type: string
                description: Message of the PingTemplate.
              url:
                type: string
                description: Optional URL.
              url_text:
                type: string
                description: Optional text for the URL.
              reminder_latency:
                type: string
                description: Latency before a reminder.
              expire_latency:
                type: string
                description: Latency before expiration.
              schedule:
                type: array
                items:
                  type: object
    responses:
      201:
        description: PingTemplate created successfully.
      403:
        description: No access to the study.
      404:
        description: User not found.
      500:
        description: Error creating PingTemplate.
    """
    current_app.logger.info(f"POST request to create ping_template, study_id={study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Ensure user can edit this study
    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(f"User {user.id} lacks edit permission on study {study_id}.")
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
            study_id=study_id,
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

    current_app.logger.info(f"User created ping template ID={pt.id} in study={study_id}")
    return jsonify({
        "message": "Ping Template created successfully",
        "ping_template": pt.to_dict()
    }), 201


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_single_ping_template(study_id: int, template_id: int) -> Any:
    """
    Retrieve a single PingTemplate by its ID under a specific study.

    ---
    parameters:
      - name: study_id
        in: path
        type: integer
        required: true
        description: The ID of the study.
      - name: template_id
        in: path
        type: integer
        required: true
        description: The ID of the PingTemplate.
    responses:
      200:
        description: PingTemplate retrieved successfully.
      403:
        description: No access to the study.
      404:
        description: PingTemplate not found or user not found.
      500:
        description: Error retrieving PingTemplate.
    """
    current_app.logger.info(f"GET single ping_template {template_id} in study {study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check permission
    study = user_has_study_permission(user.id, study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(f"User {user.id} has no access to study {study_id}")
        return jsonify({"error": f"No access to study {study_id}"}), 403

    pt = PingTemplate.query.filter_by(id=template_id, study_id=study_id).first()
    if not pt:
        return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

    current_app.logger.info(f"Returning ping_template {template_id} for study {study_id}")
    return jsonify(pt.to_dict()), 200

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_ping_template(study_id: int, template_id: int) -> Any:
    """
    Update an existing PingTemplate under a study. Requires 'editor' role or higher.

    ---
    parameters:
      - name: study_id
        in: path
        type: integer
        required: true
        description: The ID of the study.
      - name: template_id
        in: path
        type: integer
        required: true
        description: The ID of the PingTemplate.
    requestBody:
      description: JSON payload with the fields to update.
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: Updated name of the PingTemplate.
              message:
                type: string
                description: Updated message of the PingTemplate.
              url:
                type: string
                description: Updated URL.
              url_text:
                type: string
                description: Updated text for the URL.
              reminder_latency:
                type: string
                description: Updated latency before a reminder.
              expire_latency:
                type: string
                description: Updated latency before expiration.
              schedule:
                type: array
                items:
                  type: object
    responses:
      200:
        description: PingTemplate updated successfully.
      403:
        description: No access to the study.
      404:
        description: PingTemplate not found or user not found.
      500:
        description: Error updating PingTemplate.
    """
    current_app.logger.info(f"PUT request to update ping_template {template_id} in study {study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(f"User {user.id} lacks edit permission on study {study_id}.")
        return jsonify({"error": f"No access to study {study_id}"}), 403

    pt = PingTemplate.query.filter_by(id=template_id, study_id=study_id).first()
    if not pt:
        return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

    data = request.get_json()
    for field in ["name", "message", "url", "url_text", "reminder_latency", "expire_latency", "schedule"]:
        if field in data:
            setattr(pt, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping_template {template_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error updating PingTemplate"}), 500

    current_app.logger.info(f"Ping template {template_id} in study {study_id} updated successfully.")
    return jsonify({
        "message": "Ping Template updated successfully",
        "ping_template": pt.to_dict()
    }), 200


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_ping_template(study_id: int, template_id: int) -> Any:
    """
    Delete a PingTemplate from a study. Requires 'editor' role or higher.

    ---
    parameters:
      - name: study_id
        in: path
        type: integer
        required: true
        description: The ID of the study.
      - name: template_id
        in: path
        type: integer
        required: true
        description: The ID of the PingTemplate to delete.
    responses:
      200:
        description: PingTemplate deleted successfully.
      403:
        description: No access to the study.
      404:
        description: PingTemplate not found or user not found.
      500:
        description: Error deleting PingTemplate.
    """
    current_app.logger.info(f"DELETE ping_template {template_id} in study {study_id}")

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(f"User {user.id} has no edit access to study {study_id}")
        return jsonify({"error": f"No access to study {study_id}"}), 403

    pt = PingTemplate.query.filter_by(id=template_id, study_id=study_id).first()
    if not pt:
        return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

    try:
        db.session.delete(pt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping_template {template_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error deleting PingTemplate"}), 500

    current_app.logger.info(f"Ping template {template_id} deleted from study {study_id}.")
    return jsonify({"message": f"Ping Template {template_id} deleted successfully."}), 200