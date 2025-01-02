# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS
from sqlalchemy.orm import Query
from flask_redis import FlaskRedis


class SoftDeleteQuery(Query):
    """
    A custom query class that automatically excludes rows
    where deleted_at is not null, unless explicitly stated.

    To include soft-deleted rows, use the with_deleted() method.
    MyModel.query.with_deleted().all()
    """
    _with_deleted = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def with_deleted(self):
        """
        Chainable method that disables the soft-delete filter,
        returning all records (including soft-deleted).
        """
        self._with_deleted = True
        return self

    def _apply_deleted_criteria(self):
        """
        Add filters to exclude rows whose deleted_at is not null
        for all mapped classes that have deleted_at.
        """
        for entity in self._mapper_entities:
            model = entity.mapper.class_
            # Only apply filter if the model actually has 'deleted_at'
            if hasattr(model, 'deleted_at'):
                self = self.filter(model.deleted_at.is_(None))
        return self

    def __iter__(self):
        """
        Overridden to apply the soft-delete filter right before iteration.
        """
        if not self._with_deleted:
            self = self._apply_deleted_criteria()
        return super().__iter__()

# Create the global Flask extensions
db = SQLAlchemy(query_class=SoftDeleteQuery)
migrate = Migrate()
jwt = JWTManager()
swagger = Swagger()
cors = CORS()
redis_client = FlaskRedis()

def init_extensions(app):
    global celery

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": [
                "http://emapingbot.com",
                "https://emapingbot.com", 
                "http://localhost:3000",  # Allow localhost for local testing
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"],
            "supports_credentials": True,  
        }
    })
    swagger.init_app(app)
    redis_client.init_app(app)
