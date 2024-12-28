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

ping_templates_bp = Blueprint('ping_templates', __name__)


@ping_templates_bp.route('/studies/<int:study_id>/ping_templates', methods=['GET'])
@jwt_required()
def get_ping_templates(study_id):
    current_app.logger.debug(f"Entered get_ping_templates route for study_id={study_id}.")

    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to fetch ping templates.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user.id, study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(
            f"User {user.id} lacks 'viewer' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    stmt = (
        db.session.query(PingTemplate)
        .filter_by(study_id=study_id)
        .filter(PingTemplate.deleted_at.is_(None))
        .order_by(PingTemplate.id.asc())
        .statement
    )

    pagination = paginate_statement(db.session, stmt, page=page, per_page=per_page)

    ping_templates = [
        {
            "id": pt.id,
            "name": pt.name,
            "message": pt.message,
            "url": pt.url,
            "url_text": pt.url_text,
            "reminder_latency": str(pt.reminder_latency) if pt.reminder_latency else None,
            "expire_latency": str(pt.expire_latency) if pt.expire_latency else None,
            "schedule": pt.schedule,
        }
        for pt in pagination["items"]
    ]

    current_app.logger.info(
        f"User {user.id} fetched {len(ping_templates)} ping templates for study {study_id} "
        f"on page {page}/{pagination['pages']}."
    )

    return jsonify({
        "data": ping_templates,
        "meta": {
            "page": pagination["page"],
            "per_page": pagination["per_page"],
            "total": pagination["total"],
            "pages": pagination["pages"]
        }
    }), 200


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
            f"User {user.id} lacks 'viewer' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    pt = get_ping_template_by_id(db.session, template_id)
    if not pt or pt.deleted_at is not None or pt.study_id != study_id:
        current_app.logger.warning(
            f"Ping template ID={template_id} not found or inaccessible for study_id={study_id}."
        )
        return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

    current_app.logger.info(
        f"User {user.id} fetched ping template ID={template_id} for study {study_id}."
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
            f"User {user.id} lacks 'editor' permission for study_id={study_id}."
        )
        return jsonify({"error": f"No access to study {study_id}"}), 403

    data = request.get_json()

    try:
        updated_ping_template = update_ping_template(db.session, template_id, **data)
        if not updated_ping_template or updated_ping_template.deleted_at is not None:
            current_app.logger.warning(
                f"Ping template ID={template_id} not found or inaccessible for study_id={study_id}."
            )
            return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

        db.session.commit()
        current_app.logger.info(
            f"User {user.id} updated ping template ID={template_id} for study {study_id}."
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
            return jsonify({"error": f"PingTemplate {template_id} not found"}), 404

        db.session.commit()
        current_app.logger.info(
            f"User {user.id} deleted ping template ID={template_id} for study {study_id}."
        )
        return jsonify({"message": f"Ping Template {template_id} deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping template ID={template_id} for study_id={study_id}.")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500