from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, UserStudy
from utils import generate_non_confusable_code

studies_bp = Blueprint('studies', __name__)

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

@studies_bp.route('/studies', methods=['GET'])
@jwt_required()
def get_studies():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(f"User {user.email} requested studies.")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = (
        db.session.query(Study)
        .join(UserStudy)
        .filter(UserStudy.user_id == user.id)
        .order_by(Study.id.asc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    studies_list = [
        {"id": st.id, "public_name": st.public_name, "internal_name": st.internal_name, "code": st.code}
        for st in pagination.items
    ]

    current_app.logger.info(f"User {user.email} fetched {len(studies_list)} studies.")

    return jsonify({
        "data": studies_list,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200

@studies_bp.route('/studies', methods=['POST'])
@jwt_required()
def create_study():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    public_name = data.get('public_name')
    internal_name = data.get('internal_name')
    contact_message = data.get('contact_message')
    role = "owner"

    if not public_name or not internal_name:
        current_app.logger.error("Missing required fields: public_name or internal_name.")
        return jsonify({"error": "Missing required fields: public_name, internal_name"}), 400
    
    # Generate a unique study code used for signups
    study_code = None
    while not study_code:
        code = generate_non_confusable_code(length=8)
        if not Study.query.filter_by(code=code).first():
            study_code = code

    # Create the new study 
    try:
        new_study = Study(public_name=public_name, 
                          internal_name=internal_name, 
                          code=study_code,
                          contact_message=contact_message)
        db.session.add(new_study)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating study")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500
    
    # Add the user as the owner of the study
    try:
        user_study = UserStudy(user_id=user.id, study_id=new_study.id, role=role)
        db.session.add(user_study)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding user {user.id} as owner of study {new_study.id}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

    current_app.logger.info(f"User {user.email} created a new study with ID {new_study.id}.")

    return jsonify({
        "message": "Study created successfully",
        "study": {"id": new_study.id, "public_name": new_study.public_name, "internal_name": new_study.internal_name, "code": new_study.code}
    }), 201

@studies_bp.route('/studies/<int:study_id>', methods=['GET'])
@jwt_required()
def get_single_study(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        current_app.logger.warning(f"Study {study_id} not found or user {user.id} has no access.")
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    current_app.logger.info(f"User {user.email} accessed study {study_id}.")
    return jsonify({
        "id": study.id, 
        "public_name": study.public_name, 
        "internal_name": study.internal_name,
        "code": study.code
        }), 200

@studies_bp.route('/studies/<int:study_id>', methods=['PUT'])
@jwt_required()
def update_study(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        current_app.logger.warning(f"Study {study_id} not found or user {user.id} has no access.")
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    data = request.get_json()
    if 'public_name' in data:
        study.public_name = data['public_name']
    if 'internal_name' in data:
        study.internal_name = data['internal_name']

    db.session.commit()

    current_app.logger.info(f"User {user.email} updated study {study_id}.")
    return jsonify({
        "message": "Study updated successfully",
        "study": {"id": study.id, "public_name": study.public_name, "internal_name": study.internal_name}
    }), 200

@studies_bp.route('/studies/<int:study_id>', methods=['DELETE'])
@jwt_required()
def delete_study(study_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    study = user_owns_study(user, study_id)
    if not study:
        current_app.logger.warning(f"Study {study_id} not found or user {user.id} has no access.")
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404

    db.session.delete(study)
    db.session.commit()

    current_app.logger.info(f"User {user.email} deleted study {study_id}.")
    return jsonify({"message": f"Study {study_id} deleted successfully."}), 200
