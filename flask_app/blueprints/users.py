
from flask import Blueprint, request, jsonify, Response, current_app, g
import hashlib
from blueprints.ping_templates import ping_templates_bp
from blueprints.studies import studies_bp
from blueprints.participants import participants_bp
from blueprints.pings import pings_bp

from hmac import compare_digest

users_bp = Blueprint('users_bp', __name__)

users_bp.register_blueprint(ping_templates_bp, url_prefix='/ping_templates')
users_bp.register_blueprint(studies_bp, url_prefix='/studies')
users_bp.register_blueprint(participants_bp, url_prefix='/participants')
users_bp.register_blueprint(pings_bp, url_prefix='/pings')

@users_bp.before_request
def check_authentication():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(response='Malformed authentication', status=401)
    
    # Get token from header
    token = auth_header.split(" ")[1]
    
    # Query DynamoDB for token
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    response = current_app.table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={
            ':pk': f'TOKEN#{token_hash}'
        }
    )
    
    # Check if token is in database
    if not response['Items']:
        return Response(response='Invalid token', status=401)
    
    # Save user_id to g
    user_id = response['Items'][0]['SK']
    g.user_id = user_id
    


    
    
    