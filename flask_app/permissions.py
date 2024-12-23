from flask import current_app
from models import UserStudy, Study, User

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


