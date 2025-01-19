# permissions.py

from flask import current_app
from typing import List, Literal
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select
from extensions import db
from models import UserStudy, Study, User

roles = {
    'developer': 0,
    'owner': 1,
    'editor': 2,
    'viewer': 3
}

def check_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user's role is <= (has enough privileges) the required role.
    """
    return roles.get(user_role, 999) <= roles.get(required_role, 999)

def get_studies_for_admin() -> List[Study]:
    """
    Return all studies (e.g., used by admin). 
    Adjust if you only want non-deleted or certain filters.
    """
    stmt = select(Study)
    results = db.session.execute(stmt)
    studies = results.scalars().all()
    return studies

def get_studies_for_user(user_id: int, minimum_role: str = "owner") -> List[Study]:
    """
    Retrieve all studies to which this user has at least `minimum_role` permission.
    """
    accepted_roles = [r for r in roles if roles[r] <= roles[minimum_role]]

    # First, find all UserStudy entries for this user with an accepted role
    stmt = (
        select(UserStudy)
        .where(
            UserStudy.user_id == user_id,
            UserStudy.role.in_(accepted_roles),
            UserStudy.deleted_at.is_(None)
        )
    )
    results = db.session.execute(stmt)
    user_studies = results.scalars().all()

    # Return the associated Study objects
    return [us.study for us in user_studies]

def get_current_user() -> User:
    """
    Retrieve the current user from the JWT identity.
    Returns None if no user is found or if identity is missing.
    """
    user_id = get_jwt_identity()
    if not user_id:
        current_app.logger.warning("JWT identity is missing.")
        return None
    
    user = db.session.get(User, user_id)
    if not user:
        current_app.logger.warning(f"User with id {user_id} not found.")
    return user

def user_has_study_permission(
    user_id: int, 
    study_id: int, 
    minimum_role: Literal["developer","owner","editor","viewer"] = "owner"
) -> Study:
    """
    Check if a user has at least `minimum_role` on a given study. 
    Return the Study object if yes, else None.
    """
    accepted_roles = [r for r in roles if roles[r] <= roles[minimum_role]]

    # Query for UserStudy entry with an accepted role
    stmt = (
        select(UserStudy)
        .where(
            UserStudy.user_id == user_id,
            UserStudy.study_id == study_id,
            UserStudy.role.in_(accepted_roles),
            UserStudy.deleted_at.is_(None)
        )
    )

    result = db.session.execute(stmt)
    user_study = result.scalar_one_or_none()

    # Return the associated Study if found
    if user_study:
        study = user_study.study
        # Attach the user's role as a temporary attribute on the study
        study._user_role = user_study.role
        return study
    
    return None