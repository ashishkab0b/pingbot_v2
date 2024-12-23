import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Interval

from app import db, create_app

load_dotenv()

# ------------------------------------------------
# Enrollments Table (Participants ↔ Studies with attributes)
# ------------------------------------------------
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    telegram_id = db.Column(db.String(100), nullable=True, unique=False)
    tz = db.Column(db.String(50), nullable=False)
    # participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), nullable=False)
    study_pid = db.Column(db.String(255), nullable=False)  # Participant ID in the study assigned by researcher
    enrolled = db.Column(db.Boolean, default=True, nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    pr_completed = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Relationships
    pings = db.relationship("Ping", back_populates="enrollment")
    study = db.relationship("Study", back_populates="enrollments")
    

# ------------------------------------------------
# UserStudy Table (Users ↔ Studies with attributes)
# ------------------------------------------------
class UserStudy(db.Model):
    __tablename__ = 'user_studies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), nullable=False)
    role = db.Column(db.String(255), nullable=False)  # e.g. 'owner': sharing + editing + viewing, 'editor': editing + viewing, 'viewer': viewing only
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="user_studies")
    study = db.relationship("Study", back_populates="user_studies")

# ------------------------------------------------
# Users Table
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
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Many-to-many relationship with Study
    user_studies = db.relationship(
        "UserStudy",
        back_populates="user"
    )

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

# ------------------------------------------------
# Studies Table
# ------------------------------------------------
class Study(db.Model):
    __tablename__ = 'studies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_name = db.Column(db.String(255), nullable=False)
    internal_name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False, unique=True)
    contact_message = db.Column(db.Text)  # e.g., "Please contact the study team for any questions or concerns by emailing ashm@stanford.edu."
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Relationships
    ping_templates = db.relationship("PingTemplate", back_populates="study")
    pings = db.relationship("Ping", back_populates="study")
    enrollments = db.relationship(
        "Enrollment",
        back_populates="study"
    )
    user_studies = db.relationship(
        "UserStudy",
        back_populates="study"
    ) 
# ------------------------------------------------
# Participants Table
# ------------------------------------------------
# class Participant(db.Model):
#     __tablename__ = 'participants'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     telegram_id = db.Column(db.String(100), nullable=True, unique=True)
#     tz = db.Column(db.String(50), nullable=False)
#     created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
#     updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

#     # Relationships
#     pings = db.relationship("Ping", back_populates="participant")
#     enrollments = db.relationship("Enrollment", back_populates="participant")

# ------------------------------------------------
# PingTemplates Table
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
    schedule = db.Column(JSONB, nullable=True)  # e.g.,  [{"start_day_num": 1, "start_time": "09:00", "end_day_num": 1, "end_time": "10:00"}, {"day_num": 2, "start_time": "09:00", "end_time": "10:00"}]
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Relationships
    study = db.relationship("Study", back_populates="ping_templates")
    pings = db.relationship("Ping", back_populates="ping_template")

# ------------------------------------------------
# Pings Table
# ------------------------------------------------
class Ping(db.Model):
    __tablename__ = 'pings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), nullable=False)
    ping_template_id = db.Column(db.Integer, db.ForeignKey('ping_templates.id'), nullable=False)
    # participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    scheduled_ts = db.Column(db.DateTime(timezone=True), nullable=False)
    expire_ts = db.Column(db.DateTime(timezone=True))
    reminder_ts = db.Column(db.DateTime(timezone=True))
    day_num = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=True)
    ping_sent = db.Column(db.Boolean, nullable=False, default=False)
    reminder_sent = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    # Relationships
    study = db.relationship("Study", back_populates="pings")
    ping_template = db.relationship("PingTemplate", back_populates="pings")
    enrollment = db.relationship("Enrollment", back_populates="pings")
    # participant = db.relationship("Participant", back_populates="pings")

