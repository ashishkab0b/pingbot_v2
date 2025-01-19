# flask_app/blueprints/studies.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime, timezone

from models import Study, UserStudy
from utils import paginate_statement
from crud import (
    # user
    get_user_by_id,
    # studies
    get_studies_for_user,
    is_study_code_taken,
    create_study,
    add_user_study,
    get_user_study,
    get_study_by_id,
    update_study,
    soft_delete_study,
    soft_delete_enrollment,
    soft_delete_ping,
    soft_delete_ping_template,
    get_user_by_email,
    update_user_study_role,
    soft_delete_user_study,
    get_user_studies_for_study,
    
    
)
from permissions import get_current_user, user_has_study_permission
from utils import generate_non_confusable_code  # custom code generator
from sqlalchemy import select


studies_bp = Blueprint('studies', __name__)

@studies_bp.route('/studies', methods=['GET'])
@jwt_required()
def get_studies_route():
    """
    Get a list of studies accessible by the current user, with pagination, sorting, and searching.

    Query Parameters:
        page (int): The page number (default: 1).
        per_page (int): The number of items per page (default: 10).
        sort_by (str): The field to sort by (default: 'id').
        sort_order (str): The sort order, 'asc' or 'desc' (default: 'asc').
        search (str): A search query to filter studies by name.

    Returns:
        JSON response containing the list of studies and pagination metadata.
    """
    current_app.logger.debug("Entered get_studies route.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("Attempted to fetch studies but user not found.")
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(f"User={user.email} requested list of their studies.")

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Get search query
    search_query = request.args.get('search', None)

    try:
        # Build base query
        stmt = (
            select(Study)
            .join(UserStudy, UserStudy.study_id == Study.id)
            .where(
                UserStudy.user_id == user.id,
                UserStudy.deleted_at.is_(None),
                Study.deleted_at.is_(None)
            )
        )

        # Apply search filter
        if search_query:
            stmt = stmt.where(
                (Study.public_name.ilike(f'%{search_query}%')) |
                (Study.internal_name.ilike(f'%{search_query}%'))
            )

        # Apply sorting
        valid_sort_columns = {
            'id': Study.id,
            'public_name': Study.public_name,
            'internal_name': Study.internal_name,
            'code': Study.code,
            # Add more fields if needed
        }
        sort_column = valid_sort_columns.get(sort_by, Study.id)

        if sort_order.lower() == 'desc':
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Paginate
        pagination = paginate_statement(db.session, stmt, page=page, per_page=per_page)

        studies_list = [
            {
                "id": st.id, 
                "public_name": st.public_name, 
                "internal_name": st.internal_name,
                "contact_message": st.contact_message,
                "code": st.code
            }
            for st in pagination["items"]
        ]

        current_app.logger.info(
            f"User={user.email} fetched {len(studies_list)} studies on page {pagination['page']}/{pagination['pages']}."
        )

        return jsonify({
            "data": studies_list,
            "meta": {
                "page": pagination['page'],
                "per_page": pagination['per_page'],
                "total": pagination['total'],
                "pages": pagination['pages']
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching studies: {e}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

@studies_bp.route('/studies', methods=['POST'])
@jwt_required()
def create_study_route():
    current_app.logger.debug("Entered create_study route.")
    
    user = get_current_user()
    if not user:
        current_app.logger.error("Failed to create study - user not found.")
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    public_name = data.get('public_name')
    internal_name = data.get('internal_name')
    contact_message = data.get('contact_message')
    role = "owner"

    if not public_name or not internal_name:
        current_app.logger.error(f"User={user.email} cannot create study - missing required fields with data={data}")
        return jsonify({"error": "Missing required fields: public_name, internal_name"}), 400

    # Generate a unique study code
    study_code = None
    while not study_code:
        candidate = generate_non_confusable_code(length=8, lowercase=True, uppercase=False, digits=True)
        if not is_study_code_taken(db.session, candidate):
            study_code = candidate

    try:
        new_study = create_study(
            db.session,
            public_name=public_name,
            internal_name=internal_name,
            code=study_code,
            contact_message=contact_message
        )
        db.session.flush()  # Ensure new_study.id is available

        # Add the user as the study owner
        add_user_study(
            db.session,
            user_id=user.id,
            study_id=new_study.id,
            role=role
        )
        
        db.session.commit()

        current_app.logger.info(f"User={user.email} created a new study={new_study.id}.")
        return jsonify({
            "message": "Study created successfully",
            "study": {
                "id": new_study.id,
                "public_name": new_study.public_name,
                "internal_name": new_study.internal_name,
                "code": new_study.code
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating study with public_name={public_name}, internal_name={internal_name}, contact_message={contact_message}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


@studies_bp.route('/studies/<int:study_id>', methods=['GET'])
@jwt_required()
def get_single_study_route(study_id):
    current_app.logger.debug(f"Entered get_single_study route for study={study_id}.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while accessing a study.")
        return jsonify({"error": "User not found"}), 404

    # user_has_study_permission presumably checks the user_study relation.
    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="viewer")
    if not study:
        current_app.logger.warning(
            f"User {user.id} tried accessing study {study_id} without permissions."
        )
        return jsonify({"error": f"Study {study_id} not found or no access"}), 404
    
    # Retrieve the attached role (if any)
    user_role = getattr(study, '_user_role', None)

    current_app.logger.info(f"User={user.email} accessed study {study_id}.")
    return jsonify({
        "id": study.id, 
        "public_name": study.public_name, 
        "internal_name": study.internal_name,
        "contact_message": study.contact_message,
        "code": study.code,
        "role": user_role  
    }), 200


@studies_bp.route('/studies/<int:study_id>', methods=['PUT'])
@jwt_required()
def update_study_route(study_id):
    current_app.logger.debug(f"Entered update_study route for study={study_id}.")
    
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to update a study.")
        return jsonify({"error": "User not found"}), 404

    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User={user.email} attempted to update study={study_id} without access."
        )
        return jsonify({"error": f"Study={study_id} not found or no access"}), 404

    data = request.get_json()
    
    # Sanitize update fields
    valid_fields = ['public_name', 'internal_name', 'contact_message']
    invalid_data_keys = [k for k in data.keys() if k not in valid_fields]
    if invalid_data_keys:
        current_app.logger.warning(f"User={user.email} attempted to update study={study_id} with invalid fields: {invalid_data_keys}")
    data = {k: v for k, v in data.items() if k in valid_fields}
    
    try:
        updated_study = update_study(db.session, study_id=study.id, **data)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating study={study_id}: {str(e)}")
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500
    else:
        current_app.logger.info(f"User={user.email} updated study {study_id}.")
        return jsonify({
            "message": "Study updated successfully",
            "study": {
                "id": updated_study.id,
                "public_name": updated_study.public_name,
                "internal_name": updated_study.internal_name
            }
        }), 200


@studies_bp.route('/studies/<int:study_id>', methods=['DELETE'])
@jwt_required()
def delete_study_route(study_id):
    current_app.logger.debug(f"Entered delete_study route for study={study_id}.")
    
    # Get the current user
    user = get_current_user()
    if not user:
        current_app.logger.warning("User not found while attempting to delete a study.")
        return jsonify({"error": "User not found"}), 404

    # Check if the user has permission to delete the study
    study = user_has_study_permission(user_id=user.id, study_id=study_id, minimum_role="editor")
    if not study:
        current_app.logger.warning(
            f"User {user.id} attempted to delete study={study_id} without access."
        )
        return jsonify({"error": f"Study={study_id} not found or no access"}), 404

    try:
        # Attempt to soft-delete the study
        if not soft_delete_study(db.session, study.id):
            current_app.logger.warning(
                f"Failed to soft-delete study={study_id}. Possibly doesn't exist."
            )
            return jsonify({"error": f"Could not delete study={study_id}"}), 404
        
    except Exception as e:
        current_app.logger.error(f"Error deleting study={study_id}")
        current_app.logger.exception(e)
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


    db.session.commit()
    current_app.logger.info(f"User={user.email} deleted study={study_id}.")
    return jsonify({"message": f"Study {study_id} deleted successfully."}), 200

@studies_bp.route('/studies/<int:study_id>/add_user', methods=['POST'])
@jwt_required()
def add_user_to_study_route(study_id):
    """
    Add (or re-add) an existing user (by their email) to a study, assigning them a given role.
    Only 'owner' or 'editor' of the study is allowed to do this.
    """
    current_app.logger.debug(f"Entered add_user_to_study route for study={study_id}.")

    # 1. Ensure the current user is logged in
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Current user not found"}), 404

    # 2. Check if current user has at least 'owner' or 'editor' permissions
    #    Adjust this as needed (some orgs allow 'editor' to add users, others only 'owner').
    study_with_permissions = user_has_study_permission(
        user_id=current_user.id,
        study_id=study_id,
        minimum_role="editor"
    )
    if not study_with_permissions:
        return jsonify({"error": "You do not have permission to add users to this study."}), 403

    # 3. Get JSON body
    data = request.get_json()
    user_email = data.get('email')
    role = data.get('role', 'viewer')  # default role is 'viewer' if none provided

    if not user_email:
        return jsonify({"error": "Email is required"}), 400

    # 4. Find user in DB
    session = db.session
    try:
        user_to_add = get_user_by_email(session, user_email)
        if not user_to_add:
            # user doesn't exist
            return jsonify({"error": f"No user with email '{user_email}' exists."}), 404

        # 5. Check that study also exists
        study_obj = get_study_by_id(session, study_id)
        if not study_obj:
            return jsonify({"error": f"Study with id={study_id} not found"}), 404

        # 6. See if there's an existing user_study row
        user_study_rel = get_user_study(session, user_to_add.id, study_id, include_deleted=True)
        if user_study_rel:
            # If the relation exists (even if soft-deleted), update the role and un-delete
            user_study_rel.role = role
            user_study_rel.deleted_at = None  # un-delete if it was soft-deleted
        else:
            # Create a new user_study link
            add_user_study(session, user_to_add.id, study_id, role)

        session.commit()
        current_app.logger.info(
            f"User with email={user_email} has been added to study={study_id} with role={role}."
        )
        return jsonify({"message": f"User {user_email} added to study {study_id} with role {role}."}), 200

    except Exception as e:
        current_app.logger.error(f"Error adding user with email={user_email} to study={study_id}: {str(e)}")
        session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@studies_bp.route('/studies/<int:study_id>/users', methods=['GET'])
@jwt_required()
def get_study_users_route(study_id):
    """
    Return the list of users (and their roles) associated with this study.
    Only users with 'owner' permission on the study can view and manage.
    """
    current_app.logger.debug(f"Entered get_study_users_route for study={study_id}.")
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Current user not found"}), 404

    # Only a user with 'owner' role on this study can list/manipulate users:
    study_with_permissions = user_has_study_permission(
        user_id=current_user.id,
        study_id=study_id,
        minimum_role="owner"  # NOTE: Only owners can manage study users
    )
    if not study_with_permissions:
        return jsonify({"error": "You do not have permission to manage users for this study."}), 403

    try:
        # Query the UserStudy table to get user-role pairs, joined with User
        user_studies = get_user_studies_for_study(db.session, study_id)

        data = []
        for us in user_studies:
            data.append({
                "user_id": us.user.id,
                "email": us.user.email,
                "first_name": us.user.first_name,
                "last_name": us.user.last_name,
                "role": us.role,
            })

        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

@studies_bp.route('/studies/<int:study_id>/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_study_user_role(study_id, user_id):
    """
    Allows the 'owner' of a study to update another user's role in that study
    """
    current_app.logger.debug(f"Entered update_study_user_role for study={study_id}, user_id={user_id}.")
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Current user not found"}), 404

    # Must be an 'owner' to manage user roles
    study_with_permissions = user_has_study_permission(
        user_id=current_user.id,
        study_id=study_id,
        minimum_role="owner"
    )
    if not study_with_permissions:
        return jsonify({"error": "You do not have permission to manage users for this study."}), 403

    # Get the new role from the request body
    data = request.get_json()
    new_role = data.get('role')
    if not new_role:
        return jsonify({"error": "Missing 'role' in request"}), 400
    
    # Prevent owner from demoting self
    if current_user.id == user_id:
        # Check the user's current role in this study
        user_study_self = get_user_study(db.session, current_user.id, study_id, include_deleted=False)
        if user_study_self and user_study_self.role == "owner" and new_role != "owner":
            return jsonify({"error": "Owners cannot change their own role from owner."}), 403

    # Update the user's role
    try:
        updated_user_study = update_user_study_role(db.session, user_id, study_id, new_role)
        if not updated_user_study:
            return jsonify({"error": "User-study relation not found or user is not in this study"}), 404
        
        db.session.commit()
        return jsonify({"message": "User's role updated successfully", "role": new_role}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating user role: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    
@studies_bp.route('/studies/<int:study_id>/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_user_from_study_route(study_id, user_id):
    """
    Allows the 'owner' of a study to remove a user from the study (soft-deleting the UserStudy link).
    """
    current_app.logger.debug(f"Entered remove_user_from_study_route for study={study_id}, user_id={user_id}.")
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Current user not found"}), 404

    # Must be an 'owner' to remove a user
    study_with_permissions = user_has_study_permission(
        user_id=current_user.id,
        study_id=study_id,
        minimum_role="owner"
    )
    if not study_with_permissions:
        return jsonify({"error": "You do not have permission to remove users for this study."}), 403

    session = db.session
    try:
        success = soft_delete_user_study(session, user_id, study_id)
        if not success:
            return jsonify({"error": "Could not remove user. Relation not found."}), 404
        session.commit()
        return jsonify({"message": "User removed from study successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error removing user from study: {e}")
        session.rollback()
        return jsonify({"error": "Internal server error"}), 500