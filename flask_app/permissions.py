from flask import current_app
from models import UserStudy, Study, User
from typing import List, Literal
from flask_jwt_extended import get_jwt_identity
from app import db

roles = {
    'developer': 0,
    'owner': 1,
    'editor': 2,
    'viewer': 3
}

def check_permission(user_role, required_role):
    return roles[user_role] <= roles[required_role]

def get_studies_for_admin():
    return Study.query.all()

def get_studies_for_user(user_id, minimum_role="owner"):
    # Get all possible roles that satisfy the minimum role condition
    accepted_roles = [role for role in roles.keys() if roles[role] <= roles[minimum_role]]

    # Retrieve user studies with roles that satisfy the minimum_role
    user_studies = UserStudy.query.filter_by(user_id=user_id).filter(UserStudy.role.in_(accepted_roles)).all()
    
    # Retrieve the study objects
    studies = [user_study.study for user_study in user_studies]
    
    return studies

def get_current_user():
    """Helper function to get the current user object from the JWT.

    Returns:
        _type_: _description_
    """
    user_id = get_jwt_identity()
    if not user_id:
        current_app.logger.warning("JWT identity is missing.")
        return None
    user = db.session.get(User, user_id)
    if not user:
        current_app.logger.warning(f"User with id {user_id} not found.")
    return user


def user_has_study_permission(user_id: int, study_id: int, minimum_role: Literal["developer", "owner", "editor", "viewer"] = "owner") -> Study:
    """Check if a user has permission to access a study with a minimum role and return the study object.

    Args:
        user_id (int): ID of the user.
        study_id (int): ID of the study.
        minimum_role (Literal[&quot;developer&quot;, &quot;owner&quot;, &quot;editor&quot;, &quot;viewer&quot;], optional): Minimum required role. Defaults to "owner".

    Returns:
        Study: returns the study object if the user has permission, otherwise None
    """
    # Get all possible roles that satisfy the minimum role condition
    accepted_roles = [role for role in roles.keys() if roles[role] <= roles[minimum_role]]
    
    # Retrieve user studies with roles that satisfy the minimum_role
    user_study = UserStudy.query.filter_by(user_id=user_id, study_id=study_id).filter(UserStudy.role.in_(accepted_roles)).first()
    
    # Retrieve the study object
    study = user_study.study if user_study else None
    
    return study



