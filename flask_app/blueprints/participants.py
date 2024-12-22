from flask import Blueprint, request, g, Response
from flask_jwt_extended import jwt_required
from config import Config
import urllib.parse
from utils import generate_non_confusable_code


participants_bp = Blueprint('participants', __name__)



# @jwt_required()
# @participants_bp.route('/add_participant', methods=['POST'])
# def add_participant():
#     study_id = request.json.get('study_id')
#     study_pid = request.json.get('study_pid')
    

# @jwt_required()
# @participants_bp.route('/delete_participant', methods=['DELETE'])
# def delete_participant():
#     participant_id = request.json.get('participant_id')
#     pass

# @jwt_required()
# @participants_bp.route('/unenroll_participant', methods=['PUT'])
# def unenroll_participant():
#     participant_id = request.json.get('participant_id')
#     study_id = request.json.get('study_id')
#     pass

# @jwt_required()
# @participants_bp.route('/get_study_participants/<study_id>', methods=['GET'])
# def get_study_participants(study_id):
#     pass



@participants_bp.route('/study_signup/<str: signup_code>/', methods=['POST'])
def study_signup(signup_code):
    study_pid = request.json.get('study_pid')
    tz = request.json.get('tz')
    
    
    

def generate_telegram_link(start_msg):
    bot_name = Config.BOT_NAME
    encoded_start_msg = urllib.parse.quote_plus(start_msg)
    url = f"https://t.me/{bot_name}?start={encoded_start_msg}"
    return url
    
    

