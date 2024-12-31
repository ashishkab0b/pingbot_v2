# flask_app/blueprints/ping_templates.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from extensions import db
from permissions import get_current_user, user_has_study_permission
from crud import (
    create_ping_template,
    get_ping_template_by_id,
    update_ping_template,
    soft_delete_ping_template
)
from utils import paginate_statement
from models import PingTemplate
from sqlalchemy import select

ping_templates_bp = Blueprint('ping_templates', __name__)

@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['GET'])
@jwt_required()
def get_ping_templates(study_id):
    """
    Get a list of ping templates for a given study, with pagination, sorting, and searching.

    Args:
        study_id (int): The ID of the study.

    Query Parameters:
        page (int): The page number (default: 1).
        per_page (int): The number of items per page (default: 10).
        sort_by (str): The field to sort by (default: 'id').
        sort_order (str): The sort order, 'asc' or 'desc' (default: 'asc').
        search (str): A search query to filter ping templates by name.

    Returns:
        JSON response containing the list of ping templates and pagination metadata.
    """
    current_app.logger.debug(f"Entered get_ping_templates route for study_id={study_id}.")

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to fetch ping templates.")
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
        study = user_has_study_permission(user.id, study_id, minimum_role="viewer")
        if not study:
            current_app.logger.warning(
                f"User {user.id} lacks 'viewer' permission for study_id={study_id}."
            )
            return jsonify({"error": f"No access to study {study_id}"}), 403

        # Build base query
        stmt = select(PingTemplate).where(
            PingTemplate.study_id == study_id,
            PingTemplate.deleted_at.is_(None)
        )

        # Apply search filter
        if search_query:
            stmt = stmt.where(PingTemplate.name.ilike(f'%{search_query}%'))

        # Apply sorting
        valid_sort_columns = {
            'id': PingTemplate.id,
            'name': PingTemplate.name,
            'message': PingTemplate.message,
            # Add more fields if needed
        }
        sort_column = valid_sort_columns.get(sort_by, PingTemplate.id)

        if sort_order.lower() == 'desc':
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Paginate
        pagination = paginate_statement(session=db.session, stmt=stmt, page=page, per_page=per_page)
        items = [pt.to_dict() for pt in pagination['items']]

        current_app.logger.info(
            f"User={user.id} fetched {len(items)} ping templates for study={study_id} "
            f"on page {pagination['page']}/{pagination['pages']}."
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
        current_app.logger.error(f"Error fetching ping templates for study_id={study_id}: {e}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['POST'])
@jwt_required()
def create_ping_template_route(study_id):
    current_app.logger.debug(f"Entered create_ping_template route for study_id={study_id}.")

    user = get_current_user()
    if not user:
        current_app.logger.error("User not found while attempting to create ping template.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User {user.id} lacks 'editor' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    data = request.get_json()
    name = data.get('name')
    message = data.get('message')
    url = data.get('url')
    url_text = data.get('url_text')
    reminder_latency = data.get('reminder_latency')
    expire_latency = data.get('expire_latency')
    schedule = data.get('schedule')

    if not name or not message:
        current_app.logger.error(f"Missing required fields: name={name}, message={message}.")
        return jsonify({"error": "Missing required fields: name, message"}), 400

    try:
        new_ping_template = create_ping_template(
            db.session,
            study_id=study_id,
            name=name,
            message=message,
            url=url,
            url_text=url_text,
            reminder_latency=reminder_latency,
            expire_latency=expire_latency,
            schedule=schedule
        )
        db.session.commit()
        current_app.logger.info(f"User {user.id} created ping template ID={new_ping_template.id}.")
        return jsonify({
            "message": "Ping Template created successfully",
            "ping_template": new_ping_template.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating ping template for study_id={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_single_ping_template_route(study_id, template_id):
    current_app.logger.debug(
        f"Entered get_single_ping_template route for study_id={study_id}, template_id={template_id}."
    )

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to fetch ping template.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(
            f"User_{user.id} lacks 'viewer' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    pt = get_ping_template_by_id(db.session, template_id)
    if not pt or pt.deleted_at is not None or pt.study_id != study_id:
        current_app.logger.warning(
            f"Ping template ID={template_id} not found or inaccessible for study_id={study_id}."
        )
        return jsonify({"error": f"Ping_template_{template_id} not found"}), 404

    current_app.logger.info(
        f"User={user.id} fetched ping_template={template_id} for study_{study_id}."
    )
    return jsonify(pt.to_dict()), 200


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_ping_template_route(study_id, template_id):
    current_app.logger.debug(
        f"Entered update_ping_template route for study_id={study_id}, template_id={template_id}."
    )

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to update ping template.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.id} lacks 'editor' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study={study_id}"}), 403

    data = request.get_json()

    try:
        updated_ping_template = update_ping_template(db.session, template_id, **data)
        if not updated_ping_template or updated_ping_template.deleted_at is not None:
            current_app.logger.warning(
                f"Ping template ID={template_id} not found or inaccessible for study_id={study_id}."
            )
            return jsonify({"error": f"Ping template={template_id} not found"}), 404

        db.session.commit()
        current_app.logger.info(
            f"User={user.id} updated ping template={template_id} for study={study_id}."
        )
        return jsonify({
            "message": "Ping Template updated successfully",
            "ping_template": updated_ping_template.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping template ID={template_id} for study_id={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_ping_template_route(study_id, template_id):
    current_app.logger.debug(
        f"Entered delete_ping_template route for study_id={study_id}, template_id={template_id}."
    )

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to delete ping template.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User {user.id} lacks 'editor' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    try:
        if not soft_delete_ping_template(db.session, template_id):
            current_app.logger.warning(
                f"Ping template ID={template_id} not found or already deleted for study_id={study_id}."
            )
            return jsonify({"error": f"Ping template={template_id} not found"}), 404

        db.session.commit()
        current_app.logger.info(
            f"User={user.id} deleted ping template ID={template_id} for study={study_id}."
        )
        return jsonify({"message": f"Ping template={template_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping template ID={template_id} for study_id={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500