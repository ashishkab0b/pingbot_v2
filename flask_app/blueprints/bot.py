
from flask import Blueprint, current_app, request, Response
from hmac import compare_digest
import pytz

bot_bp = Blueprint('bot', __name__)


@bot_bp.before_request
def check_authentication():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(response='Malformed authentication', status=401)
    
    # Get token from header
    token = auth_header.split(" ")[1]
    
    if compare_digest(token, current_app.config['BOT_SECRET_KEY']):
        return Response(response='Invalid bot token', status=401)
    
@bot_bp.route('/check_participant_exists', methods=['POST'])
def check_participant_exists():
    pass

@bot_bp.route('/add_new_participant', methods=['POST'])
def add_new_participant():
    tz = request.json.get('tz')
    

@bot_bp.route('/add_participant_to_study', methods=['POST'])
def add_participant_to_study():
    pass