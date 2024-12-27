

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, UserStudy
from permissions import get_current_user, user_has_study_permission

users_bp = Blueprint('users', __name__)




@users_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    email = data.get('email', None)
    urgent = data.get('urgent', False)
    category = data.get('category', None)  # bug, feature, help, other
    message = data.get('message', None)
    
     # send to my telegram
     # upload to database
    
    