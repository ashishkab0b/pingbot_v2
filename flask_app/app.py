from logger_setup import setup_logger
import json
from flask import Flask, request, jsonify
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import redis
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
from dotenv import load_dotenv
from flask import Response
from flasgger import Swagger



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
    Swagger(app)

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
    
    # Initialize Redis
    app.redis = redis.StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        password=app.config['REDIS_PASSWORD'],
        decode_responses=True
    )
    
    # Blueprints
    # from blueprints.admin import admin_bp
    from blueprints.bot import bot_bp
    from blueprints.auth import auth_bp
    from blueprints.studies import studies_bp
    from blueprints.ping_templates import ping_templates_bp
    from blueprints.enrollments import enrollments_bp
    from blueprints.pings import pings_bp
    from blueprints.participant_facing import particpant_facing_bp
    
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(bot_bp, url_prefix='/api/bot')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(studies_bp, url_prefix='/api')
    app.register_blueprint(ping_templates_bp, url_prefix='/api')
    app.register_blueprint(enrollments_bp, url_prefix='/api')
    app.register_blueprint(pings_bp, url_prefix='/api')
    app.register_blueprint(particpant_facing_bp, url_prefix='/')
    
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

