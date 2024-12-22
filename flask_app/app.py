from logger_setup import setup_logger
import json
from flask import Flask, request, jsonify
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import boto3
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
from dotenv import load_dotenv
from flask import Response



# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger()

# Initialize PostgreSQL database
db = SQLAlchemy()

# Initialize JWT manager
jwt = JWTManager()

def create_app(config='config.Config'):
    
    app = Flask(__name__)
    CORS(app)

    # Attach logger to app
    app.logger = logger
    
    # Load config
    try:
        app.config.from_object(config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    # Extensions
    jwt.init_app(app)
    db.init_app(app)
    
    # # JWT callbacks
    # @jwt.user_identity_loader
    # def user_identity_lookup(user):
    #     """Converts user object to JSON serializable format for JWT."""
    #     return user.id

    # @jwt.user_lookup_loader
    # def user_lookup_callback(_jwt_header, jwt_data):
    #     """Loads user object from the database based on JWT identity."""
    #     from models import User
    #     identity = jwt_data["sub"]
    #     return User.query.filter_by(id=identity).one_or_none()
    
    # Blueprints
    # from blueprints.admin import admin_bp
    from blueprints.auth import auth_bp
    from blueprints.studies import studies_bp
    from blueprints.ping_templates import ping_templates_bp
    # from blueprints.users import users_bp
    # from blueprints.bot import bot_bp
    # from blueprints.participants import participants_bp
    
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(studies_bp, url_prefix='/api')
    app.register_blueprint(ping_templates_bp, url_prefix='/api')
    # app.register_blueprint(bot_bp, url_prefix='/bot')
    # app.register_blueprint(participants_bp, url_prefix='/participants')
    # app.register_blueprint(users_bp, url_prefix='/')
    
    # @app.before_request
    # def log_request():
    #     print(f"Request received: {request.method} {request.url}")
        
    # Health Check
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    # Generic error handling
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception(e)
        return {'error': str(e)}, 500
    
    return app

