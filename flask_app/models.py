import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Interval

from app import db, create_app

load_dotenv()

# ------------------------------------------------
# Many-to-many association table for users ↔ studies
# ------------------------------------------------
user_studies = db.Table(
    'user_studies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('study_id', db.Integer, db.ForeignKey('studies.id'), primary_key=True)
)

# ------------------------------------------------
# 1) Users Table
#    columns: id, email, password, first_name, last_name, institution
# ------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    institution = db.Column(db.String(255))
    last_login = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Many-to-many relationship with Study
    studies = db.relationship(
        "Study",
        secondary=user_studies,
        back_populates="users"
    )
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

# ------------------------------------------------
# 2) Studies Table
#    columns: id, public_name, internal_name
# ------------------------------------------------
class Study(db.Model):
    __tablename__ = 'studies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_name = db.Column(db.String(255), nullable=False)
    internal_name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False, unique=True)

    # One-to-many relationships
    ping_templates = db.relationship("PingTemplate", back_populates="study")
    pings = db.relationship("Ping", back_populates="study")

    # Many-to-many relationship with User
    users = db.relationship(
        "User",
        secondary=user_studies,
        back_populates="studies"
    )

# ------------------------------------------------
# 3) Participants Table
#    columns: id, telegram_id, tz
# ------------------------------------------------
class Participant(db.Model):
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.String(100), nullable=False, unique=True)
    tz = db.Column(db.String(50), nullable=False)

    # One-to-many relationship
    pings = db.relationship("Ping", back_populates="participant")

# ------------------------------------------------
# 4) PingTemplates Table
#    columns: id, name, message, url, reminder_latency,
#             expire_latency, start_day_num, schedule
# ------------------------------------------------
class PingTemplate(db.Model):
    __tablename__ = 'ping_templates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255))
    reminder_latency = db.Column(Interval)  # e.g., '1 hour', '30 minutes'
    expire_latency = db.Column(Interval)    # e.g., '24 hours'
    start_day_num = db.Column(db.Integer)
    # Use JSONB to store a JSON list of dicts (PostgreSQL only)
    schedule = db.Column(JSONB, nullable=True)

    # Relationship back to Study
    study = db.relationship("Study", back_populates="ping_templates")

    # Relationship to Pings
    pings = db.relationship("Ping", back_populates="ping_template")

# ------------------------------------------------
# 5) Pings Table
#    columns: id, scheduled_ts, expire_ts, reminder_ts, day_num, url,
#             ping_sent, reminder_sent
# ------------------------------------------------
class Ping(db.Model):
    __tablename__ = 'pings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), nullable=False)
    ping_template_id = db.Column(db.Integer, db.ForeignKey('ping_templates.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)

    # Timestamps in UTC => DateTime(timezone=True)
    scheduled_ts = db.Column(db.DateTime(timezone=True), nullable=False)
    expire_ts = db.Column(db.DateTime(timezone=True))
    reminder_ts = db.Column(db.DateTime(timezone=True))

    day_num = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255))
    ping_sent = db.Column(db.Boolean, nullable=False, default=False)
    reminder_sent = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    study = db.relationship("Study", back_populates="pings")
    ping_template = db.relationship("PingTemplate", back_populates="pings")
    participant = db.relationship("Participant", back_populates="pings")


# def drop_tables():
#     """
#     Drops all tables in the database by invoking db.drop_all()
#     within a Flask application context.
#     """
#     app = create_app()
#     with app.app_context():
#         try:
#             db.drop_all()
#             db.session.commit()
#             print("All tables dropped successfully!")
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error dropping tables: {e}")

def create_tables():
    """
    Creates all tables in the database by invoking db.create_all()
    within a Flask application context.
    """
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            db.session.commit()
            print("All tables created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating tables: {e}")

if __name__ == '__main__':
    # print("Dropping all tables...")
    # drop_tables()
    print("Creating all tables...")
    create_tables()