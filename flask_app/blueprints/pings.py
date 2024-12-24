from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db
from models import User, Ping, Study, UserStudy
from permissions import user_has_study_permission, get_current_user

pings_bp = Blueprint('pings', __name__)



@pings_bp.route('/studies/<int:study_id>/pings', methods=['GET'])
@pings_bp.route('/pings', methods=['GET'])
@jwt_required()
def get_pings(study_id=None):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    else:
        current_app.logger.info(f"User {user.email} requested pings for study {study_id}.")

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        if study_id:
            # Verify access
            study = user_has_study_permission(user_id=user.id, 
                                              study_id=study_id, 
                                              minimum_role="viewer")
            if not study:
                return jsonify({"error": f"No access to study {study_id}"}), 403

            query = Ping.query.filter_by(study_id=study.id)
        else:
            # all pings across all studies the user can access
            accessible_studies = (
                db.session.query(UserStudy.study_id)
                .filter(UserStudy.user_id == user.id)
                .subquery()
            )
            query = Ping.query.filter(Ping.study_id.in_(accessible_studies))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for p in pagination.items:
            items.append(p.to_dict())

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
        current_app.logger.error("Error retrieving pings")
        current_app.logger.exception(e)
        return jsonify({"error": "Error retrieving pings"}), 500

# @pings_bp.route('/pings', methods=['POST'])
# @jwt_required()
# def create_ping():
#     """
#     POST /pings
#     Requires study_id. The user must have access to that study.
#     Other fields are optional or required based on your model logic.
#     """
#     user = get_current_user()
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     data = request.get_json()
#     study_id = data.get('study_id')

#     # Check user has access to this study
#     study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
#     if not study:
#         return jsonify({"error": "No access to study"}), 403

#     # Required fields for pings
#     enrollment_id = data.get('enrollment_id')
#     scheduled_ts = data.get('scheduled_ts')  # e.g. "2024-01-01T09:00:00"
#     day_num = data.get('day_num')

#     if not all([study_id, enrollment_id, scheduled_ts, day_num]):
#         return jsonify({"error": "Missing required fields: study_id, enrollment_id, scheduled_ts, day_num"}), 400

#     # Optional
#     ping_template_id = data.get('ping_template_id')
#     message = data.get('message')
#     url = data.get('url')
#     expire_ts = data.get('expire_ts')
#     reminder_ts = data.get('reminder_ts')

#     try:
#         new_ping = Ping(
#             study_id=study_id,
#             ping_template_id=ping_template_id,
#             enrollment_id=enrollment_id,
#             scheduled_ts=scheduled_ts,
#             expire_ts=expire_ts,
#             reminder_ts=reminder_ts,
#             day_num=day_num,
#             message=message,
#             url=url
#         )
#         db.session.add(new_ping)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error("Error creating ping")
#         current_app.logger.exception(e)
#         return jsonify({"error": "Internal server error"}), 500

#     current_app.logger.info(f"User {user.email} created a new ping with ID {new_ping.id}.")
#     return jsonify({
#         "message": "Ping created successfully",
#         "ping": {
#             "id": new_ping.id,
#             "study_id": new_ping.study_id,
#             "ping_template_id": new_ping.ping_template_id,
#             "enrollment_id": new_ping.enrollment_id,
#             "scheduled_ts": new_ping.scheduled_ts.isoformat() if new_ping.scheduled_ts else None,
#             "expire_ts": new_ping.expire_ts.isoformat() if new_ping.expire_ts else None,
#             "reminder_ts": new_ping.reminder_ts.isoformat() if new_ping.reminder_ts else None,
#             "day_num": new_ping.day_num,
#             "message": new_ping.message,
#             "url": new_ping.url,
#             "ping_sent": new_ping.ping_sent,
#             "reminder_sent": new_ping.reminder_sent
#         }
#     }), 201

@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['GET'])
@jwt_required()
def get_single_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404

    return jsonify(p.to_dict()), 200

@pings_bp.route('/studies/<int:study_id>/pings', methods=['POST'])
@jwt_required()
def create_ping(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    data = request.get_json()
    # minimal required fields
    enrollment_id = data.get('enrollment_id')
    scheduled_ts = data.get('scheduled_ts')
    day_num = data.get('day_num')

    if not all([enrollment_id, scheduled_ts, day_num]):
        return jsonify({"error": "Missing required fields: enrollment_id, scheduled_ts, day_num"}), 400

    # optional
    ping_template_id = data.get('ping_template_id')
    message = data.get('message')
    url = data.get('url')
    expire_ts = data.get('expire_ts')
    reminder_ts = data.get('reminder_ts')

    try:
        new_ping = Ping(
            study_id=study.id,
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
        current_app.logger.error(f"Error creating ping in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error creating ping"}), 500

    return jsonify({
        "message": "Ping created successfully",
        "ping": new_ping.to_dict()
    }), 201

@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['PUT'])
@jwt_required()
def update_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404

    data = request.get_json()
    # update any provided fields
    for field in ["ping_template_id", "enrollment_id", "scheduled_ts", "expire_ts",
                  "reminder_ts", "day_num", "message", "url", "ping_sent", "reminder_sent"]:
        if field in data:
            setattr(p, field, data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ping {ping_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error updating ping"}), 500

    return jsonify({"message": "Ping updated", "ping": p.to_dict()}), 200


@pings_bp.route('/studies/<int:study_id>/pings/<int:ping_id>', methods=['DELETE'])
@jwt_required()
def delete_ping(study_id, ping_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        return jsonify({"error": f"No access to study {study_id}"}), 403

    p = Ping.query.filter_by(id=ping_id, study_id=study.id).first()
    if not p:
        return jsonify({"error": "Ping not found or no access"}), 404

    try:
        db.session.delete(p)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ping {ping_id} in study {study_id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Error deleting ping"}), 500

    return jsonify({"message": f"Ping {ping_id} deleted successfully."}), 200