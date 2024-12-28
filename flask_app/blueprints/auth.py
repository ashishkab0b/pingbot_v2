from flask import (
    Blueprint, 
    request, 
    current_app, 
    Response, 
    jsonify
)
from datetime import datetime
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import redis

from config import CurrentConfig
from models import User
from extensions import db, jwt

auth_bp = Blueprint('auth', __name__)

@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    """
    Check if the given JWT is blacklisted (logged out).
    """
    jti = jwt_payload["jti"]
    redis_client = current_app.redis
    entry = redis_client.get(f"blacklisted_{jti}")
    return entry is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    institution = data.get('institution')

    current_app.logger.info("Register endpoint accessed")

    if not email or not password or not first_name or not last_name or not institution:
        current_app.logger.warning("Missing required fields in registration data")
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        current_app.logger.warning(f"Registration attempt for existing user: {email}")
        return jsonify({'message': 'User already exists'}), 400

    try:
        user = User(email=email, first_name=first_name, last_name=last_name, institution=institution)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"User registered successfully: {email}")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        current_app.logger.error(f"Error registering user: {email}, error: {e}")
        return jsonify({'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    current_app.logger.info("Login endpoint accessed")

    if not email or not password:
        current_app.logger.warning("Missing email or password in login request")
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        current_app.logger.info(f"User logged in successfully: {email}")
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    # Update last_login timestamp in user table
    user.last_login = datetime.now()
    db.session.commit()
    

    current_app.logger.warning(f"Invalid login attempt for email: {email}")
    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_app.logger.info("Token refresh endpoint accessed")
    try:
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        current_app.logger.info(f"Access token refreshed for user: {current_user}")
        return jsonify({'access_token': new_access_token}), 200
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {e}")
        return jsonify({'message': 'Token refresh failed'}), 500
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Blacklist the current JWT so that it cannot be used again.
    """
    jti = get_jwt()['jti']  # Unique identifier for JWT
    # You can store other info like 'exp' in the token if you want to set a shorter TTL.
    current_app.logger.info(f"Blacklisting token with jti: {jti}")

    # Add to Redis with an expiration time. 
    # It's recommended to match or exceed the JWT_ACCESS_TOKEN_EXPIRES time.
    current_app.redis.setex(f"blacklisted_{jti}", current_app.config["JWT_ACCESS_TOKEN_EXPIRES"], "true")

    return jsonify({"message": "Successfully logged out"}), 200