
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from logger_setup import setup_logger
from sqlalchemy.orm import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import render_template_string

# Import extensions
from extensions import db, migrate, jwt, swagger, cors, redis_client, init_extensions
from config import CurrentConfig

def create_app(config):
    # Load environment variables
    load_dotenv()

    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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
    from blueprints.support import support_bp
    from blueprints.bot import bot_bp
    from blueprints.auth import auth_bp
    from blueprints.studies import studies_bp
    from blueprints.ping_templates import ping_templates_bp
    from blueprints.enrollments import enrollments_bp
    from blueprints.pings import pings_bp
    from blueprints.participant_facing import particpant_facing_bp

    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(bot_bp, url_prefix='/api/bot')
    app.register_blueprint(support_bp, url_prefix='/api')
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
    
    @app.route("/smash_matchups", )
    def smash_matchups():
        matchups = [
            {"character": "Ike", "best_matchup": "Bowser", "worst_matchup": "Jigglypuff"},
            {"character": "Ike", "best_matchup": "King Dedede", "worst_matchup": "Kirby"},
        ]

        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Smash Ultimate Matchups</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 20px;
                    background-color: #f4f4f9;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                th {
                    background-color: #6c757d;
                    color: white;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
            </style>
        </head>
        <body>
            <h1>Super Smash Bros. Ultimate: Ike Matchups</h1>
            <table>
                <thead>
                    <tr>
                        <th>Character</th>
                        <th>Best Matchup</th>
                        <th>Worst Matchup</th>
                    </tr>
                </thead>
                <tbody>
                    {% for matchup in matchups %}
                    <tr>
                        <td>{{ matchup.character }}</td>
                        <td>{{ matchup.best_matchup }}</td>
                        <td>{{ matchup.worst_matchup }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """

        return render_template_string(html_template, matchups=matchups)

    return app