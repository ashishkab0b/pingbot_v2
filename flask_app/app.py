
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from logger_setup import setup_logger
from sqlalchemy.orm import Session

# Import extensions
from extensions import db, migrate, jwt, swagger, cors, redis_client, init_extensions
from config import CurrentConfig

def create_app(config):
    # Load environment variables
    load_dotenv()

    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize logger
    logger = setup_logger()
    app.logger = logger

    # Initialize Flask extensions
    init_extensions(app)
    
    # Initialize Celery
    from celery_factory import make_celery
    celery = make_celery(app)
    app.celery = celery # Add celery to app context    

    # Import models AFTER db is set up
    from models import User, Study, PingTemplate, UserStudy, Ping, Enrollment, Support

    # Register Blueprints
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
    app.register_blueprint(particpant_facing_bp, url_prefix='/api')

    # Health Check
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    # Log all requests
    # @app.before_request
    # def log_request():
    #     logger.info(f"{request.method} {request.url}")
        

    # Error Handlers    
    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({
            'error': 'Unauthorized access'
        }), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expired'
        }), 401
        
    @app.errorhandler(404)
    def not_found_error(e):
        logger.warning(f"404 Not Found: {request.method} {request.url}")
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.error(f"HTTPException: {e.description} ({e.code}) at {request.method} {request.url}")
        return {'error': e.description}, e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception(f"Unhandled Exception at {request.method} {request.url}")
        return {'error': 'Internal server error'}, 500

    return app