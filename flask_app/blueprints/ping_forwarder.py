from flask import Blueprint, request, jsonify, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Study, PingTemplate, UserStudy, Ping

ping_router_bp = Blueprint('ping_router', __name__)


@ping_router_bp.route('/ping/<ping_id>', methods=['GET'])
def ping_forwarder(ping_id):
    """
    Forward a ping to the appropriate URL.
    :param ping_id: The ID of the ping to forward.
    
    
    """
    # Log the start of the request
    current_app.logger.info("Received request to forward ping.")
    
    # Get the ping
    ping = Ping.query.get(ping_id)
    
    # Check if the ping exists
    if not ping:
        current_app.logger.error(f"Failed to find ping with ID {ping_id}.")
        return jsonify({"error": "Ping not found."}), 404
    
    # Get query variable: code
    code = request.args.get('code')
    
    # Check if code is present and matches the ping's code
    if not code or code != ping.forwarding_code:
        current_app.logger.error(f"Invalid forwarding code: {code}.")
        return jsonify({"error": "Invalid code."}), 400
    
    # Redirect to ping.url
    return redirect(ping.url)
    
    
    
    
    