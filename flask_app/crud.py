# crud.py

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models import (
    User,
    Study,
    UserStudy,
    Enrollment,
    Ping,
    PingTemplate,
    Support
)

# ======================= USERS =======================
def get_user_by_id(
    session: Session, 
    user_id: int, 
    include_deleted: bool = False
) -> Optional[User]:
    """
    Fetch user by ID, optionally including soft-deleted users.
    """
    stmt = select(User).where(User.id == user_id)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_user_by_email(
    session: Session, 
    email: str, 
    include_deleted: bool = False
) -> Optional[User]:
    """
    Fetch user by email, optionally including soft-deleted users.
    """
    stmt = select(User).where(User.email == email)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def create_user(
    session: Session,
    email: str,
    password: str,
    **kwargs
) -> User:
    """
    Create and return a new User record (uncommitted).
    """
    user = User(
        email=email,
        first_name=kwargs.get('first_name'),
        last_name=kwargs.get('last_name'),
        institution=kwargs.get('institution'),
        prolific_token=kwargs.get('prolific_token')
    )
    user.set_password(password)
    session.add(user)
    return user


def update_user(
    session: Session, 
    user_id: int, 
    **kwargs
) -> Optional[User]:
    """
    Update a User record and return it (uncommitted).
    """
    user = get_user_by_id(session, user_id, include_deleted=True)
    if not user:
        return None

    for field in ["email", "first_name", "last_name", "institution", "prolific_token"]:
        if field in kwargs:
            setattr(user, field, kwargs[field])

    if 'password' in kwargs:
        user.set_password(kwargs['password'])

    return user


def soft_delete_user(session: Session, user_id: int) -> bool:
    """
    Soft-delete a User by setting deleted_at.
    """
    user = get_user_by_id(session, user_id, include_deleted=True)
    if not user:
        return False

    user.deleted_at = datetime.now(timezone.utc)
    return True


# ======================= STUDIES =======================
def create_study(
    session: Session,
    public_name: str,
    internal_name: str,
    code: str,
    contact_message: Optional[str] = None
) -> Study:
    """
    Create and return a Study record (uncommitted).
    """
    study = Study(
        public_name=public_name,
        internal_name=internal_name,
        code=code,
        contact_message=contact_message
    )
    session.add(study)
    return study


def get_study_by_id(
    session: Session, 
    study_id: int,
    include_deleted: bool = False
) -> Optional[Study]:
    """
    Fetch a single Study by ID, optionally including soft-deleted records.
    """
    stmt = select(Study).where(Study.id == study_id)
    if not include_deleted:
        stmt = stmt.where(Study.deleted_at.is_(None))

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_study_by_code(
    session: Session, 
    code: str,
    include_deleted: bool = False
) -> Optional[Study]:
    """
    Fetch a single Study by unique code, optionally including soft-deleted records.
    """
    stmt = select(Study).where(Study.code == code)
    if not include_deleted:
        stmt = stmt.where(Study.deleted_at.is_(None))

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def is_study_code_taken(
    session: Session,
    code: str
) -> bool:
    """
    Utility to check if a given study code is already taken.
    """
    return get_study_by_code(session, code) is not None


def update_study(
    session: Session, 
    study_id: int,
    **kwargs
) -> Optional[Study]:
    """
    Update a Study record and return it (uncommitted).
    """
    study = get_study_by_id(session, study_id, include_deleted=True)
    if not study:
        return None

    for field in ["public_name", "internal_name", "contact_message"]:
        if field in kwargs:
            setattr(study, field, kwargs[field])
    return study


def soft_delete_study(
    session: Session, 
    study_id: int
) -> bool:
    """
    Soft-delete a Study by setting deleted_at.
    """
    study = get_study_by_id(session, study_id, include_deleted=True)
    if not study:
        return False

    study.deleted_at = datetime.now(timezone.utc)
    return True


def get_studies_for_user(
    session: Session, 
    user_id: int
) -> List[Study]:
    """
    Return a list of Studies that a user is linked to (and not soft-deleted).
    """
    # You can do it with a join or subquery. For example:
    stmt = (
        select(Study)
        .join(UserStudy, Study.id == UserStudy.study_id)
        .where(
            UserStudy.user_id == user_id,
            Study.deleted_at.is_(None)
        )
        .order_by(Study.id.asc())
    )
    results = session.execute(stmt)
    return results.scalars().all()


# ========== USER-STUDY RELATION (UserStudy) ==========
def add_user_to_study(
    session: Session,
    user_id: int,
    study_id: int,
    role: str
) -> UserStudy:
    """
    Link a user to a study with a specified role (uncommitted).
    """
    user_study = UserStudy(
        user_id=user_id,
        study_id=study_id,
        role=role
    )
    session.add(user_study)
    return user_study


def get_user_study_relation(
    session: Session, 
    user_id: int, 
    study_id: int
) -> Optional[UserStudy]:
    """
    Retrieve a UserStudy record if it exists (ignoring soft-delete, if any).
    """
    stmt = (
        select(UserStudy)
        .where(
            UserStudy.user_id == user_id,
            UserStudy.study_id == study_id
        )
    )
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_user_study_role(
    session: Session, 
    user_id: int, 
    study_id: int, 
    new_role: str
) -> Optional[UserStudy]:
    """
    Update a user's role in a study (uncommitted).
    """
    user_study = get_user_study_relation(session, user_id, study_id)  
    if not user_study:
        return None

    user_study.role = new_role
    return user_study


# ======================= ENROLLMENTS =======================
def create_enrollment(
    session: Session,
    study_id: int,
    tz: str,
    study_pid: str,
    enrolled: bool,
    signup_ts_local: datetime,
    telegram_id: Optional[str] = None
) -> Enrollment:
    enrollment = Enrollment(
        study_id=study_id,
        tz=tz,
        study_pid=study_pid,
        enrolled=enrolled,
        signup_ts_local=signup_ts_local,
        telegram_id=telegram_id
    )
    session.add(enrollment)
    return enrollment


def get_enrollment_by_id(
    session: Session, 
    enrollment_id: int,
    include_deleted: bool = False
) -> Optional[Enrollment]:
    stmt = select(Enrollment).where(Enrollment.id == enrollment_id)
    if not include_deleted:
        stmt = stmt.where(Enrollment.deleted_at.is_(None))
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_enrollment(
    session: Session, 
    enrollment_id: int, 
    **kwargs
) -> Optional[Enrollment]:
    enrollment = get_enrollment_by_id(session, enrollment_id, include_deleted=True)
    if not enrollment:
        return None

    for field in ["telegram_id", "tz", "study_pid", "enrolled", "signup_ts_local", "pr_completed"]:
        if field in kwargs:
            setattr(enrollment, field, kwargs[field])
    return enrollment


def soft_delete_enrollment(session: Session, enrollment_id: int) -> bool:
    enrollment = get_enrollment_by_id(session, enrollment_id, include_deleted=True)
    if not enrollment:
        return False

    enrollment.deleted_at = datetime.now(timezone.utc)
    return True


# ======================= PING TEMPLATES =======================
def create_ping_template(
    session: Session,
    study_id: int,
    name: str,
    message: str,
    url: Optional[str] = None,
    url_text: Optional[str] = None,
    reminder_latency=None,
    expire_latency=None,
    schedule=None
) -> PingTemplate:
    pt = PingTemplate(
        study_id=study_id,
        name=name,
        message=message,
        url=url,
        url_text=url_text,
        reminder_latency=reminder_latency,
        expire_latency=expire_latency,
        schedule=schedule
    )
    session.add(pt)
    return pt


def get_ping_template_by_id(
    session: Session, 
    template_id: int,
    include_deleted: bool = False
) -> Optional[PingTemplate]:
    stmt = select(PingTemplate).where(PingTemplate.id == template_id)
    if not include_deleted:
        stmt = stmt.where(PingTemplate.deleted_at.is_(None))
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_ping_template(
    session: Session, 
    template_id: int, 
    **kwargs
) -> Optional[PingTemplate]:
    pt = get_ping_template_by_id(session, template_id, include_deleted=True)
    if not pt:
        return None

    for field in ["name", "message", "url", "url_text", "reminder_latency", "expire_latency", "schedule"]:
        if field in kwargs:
            setattr(pt, field, kwargs[field])
    return pt


def delete_ping_template(
    session: Session, 
    template_id: int
) -> bool:
    """
    Hard-delete (completely remove) a PingTemplate.
    Or switch to a soft-delete if desired.
    """
    pt = get_ping_template_by_id(session, template_id, include_deleted=True)
    if not pt:
        return False

    session.delete(pt)
    return True

def soft_delete_ping_template(
    session: Session,
    template_id: int
) -> bool:
    """
    Soft-delete a PingTemplate by setting deleted_at.
    Args:
        session (Session): _description_
        template_id (int): _description_

    Returns:
        bool: _description_
    """
    
    pt = get_ping_template_by_id(session, template_id, include_deleted=True)
    if not pt:
        return False

    pt.deleted_at = datetime.now(timezone.utc)
    return True


# ======================= PINGS =======================
def create_ping(
    session: Session,
    **kwargs
) -> Ping:
    ping = Ping(**kwargs)
    session.add(ping)
    return ping


def get_ping_by_id(
    session: Session, 
    ping_id: int,
    include_deleted: bool = False
) -> Optional[Ping]:
    stmt = select(Ping).where(Ping.id == ping_id)
    if not include_deleted:
        stmt = stmt.where(Ping.deleted_at.is_(None))
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_ping(
    session: Session, 
    ping_id: int, 
    **kwargs
) -> Optional[Ping]:
    ping = get_ping_by_id(session, ping_id, include_deleted=True)
    if not ping:
        return None

    for field in [
        "ping_template_id", "enrollment_id", "scheduled_ts", "expire_ts",
        "reminder_ts", "day_num", "message", "url", 
        "ping_sent", "reminder_sent", "first_clicked_ts", "last_clicked_ts"
    ]:
        if field in kwargs:
            setattr(ping, field, kwargs[field])
    return ping


def soft_delete_ping(
    session: Session, 
    ping_id: int
) -> bool:
    ping = get_ping_by_id(session, ping_id, include_deleted=True)
    if not ping:
        return False

    ping.deleted_at = datetime.now(timezone.utc)
    return True


def soft_delete_all_pings_for_enrollment(
    session: Session, 
    enrollment_id: int
) -> bool:
    stmt = (
        select(Ping)
        .where(Ping.enrollment_id == enrollment_id)
        .where(Ping.deleted_at.is_(None))
    )
    pings = session.execute(stmt).scalars().all()
    for ping in pings:
        ping.deleted_at = datetime.now(timezone.utc)
    return True


# ======================= SUPPORT =======================
def create_support_query(
    session: Session,
    user_id: int,
    email: str,
    messages: dict,
    query_type: str,
    is_urgent: bool = False
) -> Support:
    support = Support(
        user_id=user_id,
        email=email,
        messages=messages,
        query_type=query_type,
        is_urgent=is_urgent
    )
    session.add(support)
    return support


def get_support_by_id(
    session: Session, 
    support_id: int,
    include_deleted: bool = False
) -> Optional[Support]:
    stmt = select(Support).where(Support.id == support_id)
    if not include_deleted:
        stmt = stmt.where(Support.deleted_at.is_(None))
    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_support_query(
    session: Session, 
    support_id: int, 
    **kwargs
) -> Optional[Support]:
    support = get_support_by_id(session, support_id, include_deleted=True)
    if not support:
        return None

    for field in ["is_urgent", "resolved", "notes", "messages"]:
        if field in kwargs:
            setattr(support, field, kwargs[field])
    return support


def soft_delete_support_query(
    session: Session, 
    support_id: int
) -> bool:
    support = get_support_by_id(session, support_id, include_deleted=True)
    if not support:
        return False

    support.deleted_at = datetime.now(timezone.utc)
    return True