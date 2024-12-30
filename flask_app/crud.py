# crud.py

from typing import Optional, List, Any, Dict
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from sqlalchemy.sql import or_, and_, not_

from models import (
    User,
    Study,
    UserStudy,
    Enrollment,
    Ping,
    PingTemplate,
    Support
)

# ======================= Helper Functions =======================
def include_deleted_records(query, model, include_deleted: bool):
    """
    Helper function to include or exclude soft-deleted records in a query.

    Args:
        query: The SQLAlchemy query object.
        model: The model class (e.g., User, Study).
        include_deleted: Whether to include soft-deleted records.

    Returns:
        The modified query.
    """
    if not include_deleted:
        query = query.where(model.deleted_at.is_(None))
    return query

# ======================= USERS =======================
def get_user_by_id(
    session: Session, 
    user_id: int, 
    include_deleted: bool = False
) -> Optional[User]:
    """
    Fetch user by ID, optionally including soft-deleted users.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user to fetch.
        include_deleted (bool): Whether to include soft-deleted users.

    Returns:
        Optional[User]: The User object if found, else None.
    """
    
    stmt = select(User).where(User.id == user_id)
    stmt = include_deleted_records(stmt, User, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_user_by_email(
    session: Session, 
    email: str, 
    include_deleted: bool = False
) -> Optional[User]:
    """
    Fetch user by email, optionally including soft-deleted users.

    Args:
        session (Session): The database session.
        email (str): The email of the user to fetch.
        include_deleted (bool): Whether to include soft-deleted users.

    Returns:
        Optional[User]: The User object if found, else None.
    """
    
    stmt = select(User).where(User.email == email)
    stmt = include_deleted_records(stmt, User, include_deleted)

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

    Args:
        session (Session): The database session.
        email (str): The user's email.
        password (str): The user's password.
        **kwargs: Additional fields (first_name, last_name, institution, prolific_token).

    Returns:
        User: The newly created User object.
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

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user to update.
        **kwargs: Fields to update (email, first_name, last_name, institution, prolific_token, password).

    Returns:
        Optional[User]: The updated User object if found, else None.
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

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
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

    Args:
        session (Session): The database session.
        public_name (str): Public name of the study.
        internal_name (str): Internal name of the study.
        code (str): Unique code for the study.
        contact_message (Optional[str]): Contact message for participants.

    Returns:
        Study: The newly created Study object.
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

    Args:
        session (Session): The database session.
        study_id (int): The ID of the study to fetch.
        include_deleted (bool): Whether to include soft-deleted studies.

    Returns:
        Optional[Study]: The Study object if found, else None.
    """
    
    stmt = select(Study).where(Study.id == study_id)
    stmt = include_deleted_records(stmt, Study, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_study_by_code(
    session: Session, 
    code: str,
    include_deleted: bool = False
) -> Optional[Study]:
    """
    Fetch a single Study by unique code, optionally including soft-deleted records.

    Args:
        session (Session): The database session.
        code (str): The unique code of the study to fetch.
        include_deleted (bool): Whether to include soft-deleted studies.

    Returns:
        Optional[Study]: The Study object if found, else None.
    """
    
    stmt = select(Study).where(Study.code == code)
    stmt = include_deleted_records(stmt, Study, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def is_study_code_taken(
    session: Session,
    code: str
) -> bool:
    """
    Utility to check if a given study code is already taken.

    Args:
        session (Session): The database session.
        code (str): The code to check.

    Returns:
        bool: True if the code is taken, False otherwise.
    """
    return get_study_by_code(session, code) is not None


def update_study(
    session: Session, 
    study_id: int,
    **kwargs
) -> Optional[Study]:
    """
    Update a Study record and return it (uncommitted).

    Args:
        session (Session): The database session.
        study_id (int): The ID of the study to update.
        **kwargs: Fields to update (public_name, internal_name, contact_message).

    Returns:
        Optional[Study]: The updated Study object if found, else None.
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

    Args:
        session (Session): The database session.
        study_id (int): The ID of the study to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    study = get_study_by_id(session, study_id, include_deleted=True)
    if not study:
        return False

    study.deleted_at = datetime.now(timezone.utc)
    return True


def get_studies_for_user(
    session: Session, 
    user_id: int,
    include_deleted: bool = False
) -> List[Study]:
    """
    Return a list of Studies that a user is linked to.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user.
        include_deleted (bool): Whether to include soft-deleted studies.

    Returns:
        List[Study]: A list of Study objects.
    """
    
    stmt = (
        select(Study)
        .join(UserStudy, Study.id == UserStudy.study_id)
        .where(
            UserStudy.user_id == user_id
        )
        .order_by(Study.id.asc())
    )
    stmt = include_deleted_records(stmt, Study, include_deleted)

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

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user.
        study_id (int): The ID of the study.
        role (str): The role (e.g., 'owner', 'editor', 'viewer').

    Returns:
        UserStudy: The newly created UserStudy object.
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
    study_id: int,
    include_deleted: bool = False
) -> Optional[UserStudy]:
    """
    Retrieve a UserStudy record if it exists, optionally including soft-deleted relations.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user.
        study_id (int): The ID of the study.
        include_deleted (bool): Whether to include soft-deleted UserStudy records.

    Returns:
        Optional[UserStudy]: The UserStudy object if found, else None.
    """
    
    stmt = (
        select(UserStudy)
        .where(
            UserStudy.user_id == user_id,
            UserStudy.study_id == study_id
        )
    )
    stmt = include_deleted_records(stmt, UserStudy, include_deleted)

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

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user.
        study_id (int): The ID of the study.
        new_role (str): The new role to assign.

    Returns:
        Optional[UserStudy]: The updated UserStudy object if found, else None.
    """
    user_study = get_user_study_relation(session, user_id, study_id, include_deleted=True)
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
    """
    Create and return an Enrollment record (uncommitted).

    Args:
        session (Session): The database session.
        study_id (int): The ID of the study.
        tz (str): Timezone of the participant.
        study_pid (str): Participant ID assigned by the study.
        enrolled (bool): Enrollment status.
        signup_ts_local (datetime): Local signup timestamp.
        telegram_id (Optional[str]): Telegram ID of the participant.

    Returns:
        Enrollment: The newly created Enrollment object.
    """
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
    """
    Fetch an Enrollment by ID, optionally including soft-deleted enrollments.

    Args:
        session (Session): The database session.
        enrollment_id (int): The ID of the enrollment.
        include_deleted (bool): Whether to include soft-deleted enrollments.

    Returns:
        Optional[Enrollment]: The Enrollment object if found, else None.
    """
    
    stmt = select(Enrollment).where(Enrollment.id == enrollment_id)
    stmt = include_deleted_records(stmt, Enrollment, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_enrollments_by_telegram_id(
    session: Session, 
    telegram_id: int,
    include_deleted: bool = False
) -> List[Enrollment]:
    """
    Fetch a list of Enrollments by Telegram ID, optionally including soft-deleted enrollments.

    Args:
        session (Session): The database session.
        telegram_id (int): The Telegram ID to search for.
        include_deleted (bool): Whether to include soft-deleted enrollments.

    Returns:
        List[Enrollment]: A list of Enrollment objects.
    """
    
    telegram_id = str(telegram_id)
    stmt = select(Enrollment).where(Enrollment.telegram_id == telegram_id)
    stmt = include_deleted_records(stmt, Enrollment, include_deleted)

    result = session.execute(stmt)
    return result.scalars().all()


def update_enrollment(
    session: Session, 
    enrollment_id: int, 
    **kwargs
) -> Optional[Enrollment]:
    """
    Update an Enrollment record and return it (uncommitted).

    Args:
        session (Session): The database session.
        enrollment_id (int): The ID of the enrollment to update.
        **kwargs: Fields to update.

    Returns:
        Optional[Enrollment]: The updated Enrollment object if found, else None.
    """
    enrollment = get_enrollment_by_id(session, enrollment_id, include_deleted=True)
    if not enrollment:
        return None

    for field in ["telegram_id", "tz", "study_pid", "enrolled", "signup_ts_local", "pr_completed"]:
        if field in kwargs:
            setattr(enrollment, field, kwargs[field])
    return enrollment


def soft_delete_enrollment(session: Session, enrollment_id: int) -> bool:
    """
    Soft-delete an Enrollment by setting deleted_at.

    Args:
        session (Session): The database session.
        enrollment_id (int): The ID of the enrollment to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
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
    """
    Create and return a PingTemplate record (uncommitted).

    Args:
        session (Session): The database session.
        study_id (int): The ID of the study.
        name (str): Name of the ping template.
        message (str): Message content.
        url (Optional[str]): URL to include in the ping.
        url_text (Optional[str]): Text for the URL link.
        reminder_latency: Latency before sending a reminder.
        expire_latency: Latency after which the ping expires.
        schedule: Schedule for the ping.

    Returns:
        PingTemplate: The newly created PingTemplate object.
    """
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
    """
    Fetch a PingTemplate by ID, optionally including soft-deleted templates.

    Args:
        session (Session): The database session.
        template_id (int): The ID of the ping template.
        include_deleted (bool): Whether to include soft-deleted templates.

    Returns:
        Optional[PingTemplate]: The PingTemplate object if found, else None.
    """
    
    stmt = select(PingTemplate).where(PingTemplate.id == template_id)
    stmt = include_deleted_records(stmt, PingTemplate, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_ping_template(
    session: Session, 
    template_id: int, 
    **kwargs
) -> Optional[PingTemplate]:
    """
    Update a PingTemplate record and return it (uncommitted).

    Args:
        session (Session): The database session.
        template_id (int): The ID of the ping template to update.
        **kwargs: Fields to update.

    Returns:
        Optional[PingTemplate]: The updated PingTemplate object if found, else None.
    """
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

    Args:
        session (Session): The database session.
        template_id (int): The ID of the ping template to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
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
        session (Session): The database session.
        template_id (int): The ID of the ping template to soft-delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
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
    """
    Create and return a Ping record (uncommitted).

    Args:
        session (Session): The database session.
        **kwargs: Fields for the Ping.

    Returns:
        Ping: The newly created Ping object.
    """
    ping = Ping(**kwargs)
    session.add(ping)
    return ping


def get_ping_by_id(
    session: Session, 
    ping_id: int,
    include_deleted: bool = False
) -> Optional[Ping]:
    """
    Fetch a Ping by ID, optionally including soft-deleted pings.

    Args:
        session (Session): The database session.
        ping_id (int): The ID of the ping.
        include_deleted (bool): Whether to include soft-deleted pings.

    Returns:
        Optional[Ping]: The Ping object if found, else None.
    """
    
    stmt = select(Ping).where(Ping.id == ping_id)
    stmt = include_deleted_records(stmt, Ping, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def get_pings_to_send(
    session: Session,
    now: datetime=datetime.now(timezone.utc)
) -> List[Ping]:
    """
    Fetch pings due to send.

    Args:
        session (Session): The database session.
        now (datetime): The current timestamp.
    Returns:
        List[Ping]: The Ping objects if found, else empty list.
    """
    stmt = (
        select(Ping)
        .join(Enrollment, Ping.enrollment_id == Enrollment.id)  # Explicit join condition
        .where(
            Ping.sent_ts.is_(None),
            Ping.scheduled_ts <= now,
            or_(Ping.expire_ts.is_(None), Ping.expire_ts > now),
            Ping.deleted_at.is_(None),
            Enrollment.deleted_at.is_(None)
        )
    )
    return session.execute(stmt).scalars().all()


def get_pings_for_reminder(
    session: Session,
    now: datetime=datetime.now(timezone.utc)
) -> List[Ping]:
    """
    Fetch pings for which reminders are due to send.
    
    Args:
        session (Session): The database session.
        now (datetime): The current timestamp.
    Returns:
        List[Ping]: The Ping objects if found, else empty list.
    """
    stmt = (
        select(Ping)
        .join(Enrollment, Ping.enrollment_id == Enrollment.id)  # Explicit join condition
        .where(
            Ping.sent_ts.isnot(None),
            Ping.reminder_sent_ts.is_(None),
            Ping.reminder_ts <= now,
            or_(Ping.expire_ts.is_(None), Ping.expire_ts > now),
            Ping.first_clicked_ts.is_(None),
            Ping.deleted_at.is_(None),
            Enrollment.deleted_at.is_(None)
        )
    )
    return session.execute(stmt).scalars().all()
    
    
def update_ping(
    session: Session, 
    ping_id: int, 
    **kwargs
) -> Optional[Ping]:
    """
    Update a Ping record and return it (uncommitted).

    Args:
        session (Session): The database session.
        ping_id (int): The ID of the ping to update.
        **kwargs: Fields to update.

    Returns:
        Optional[Ping]: The updated Ping object if found, else None.
    """
    ping = get_ping_by_id(session, ping_id, include_deleted=True)
    if not ping:
        return None

    for field in [
        "ping_template_id", "enrollment_id", "scheduled_ts", "expire_ts",
        "reminder_ts", "day_num", 
        "ping_sent", "reminder_sent", "first_clicked_ts", "last_clicked_ts"
    ]:
        if field in kwargs:
            setattr(ping, field, kwargs[field])
    return ping


def soft_delete_ping(
    session: Session, 
    ping_id: int
) -> bool:
    """
    Soft-delete a Ping by setting deleted_at.

    Args:
        session (Session): The database session.
        ping_id (int): The ID of the ping to soft-delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    ping = get_ping_by_id(session, ping_id, include_deleted=True)
    if not ping:
        return False

    ping.deleted_at = datetime.now(timezone.utc)
    return True


def soft_delete_all_pings_for_enrollment(
    session: Session, 
    enrollment_id: int
) -> bool:
    """
    Soft-delete all Pings associated with an Enrollment.

    Args:
        session (Session): The database session.
        enrollment_id (int): The ID of the enrollment.

    Returns:
        bool: True if any pings were soft-deleted, False otherwise.
    """
    
    stmt = (
        select(Ping)
        .where(Ping.enrollment_id == enrollment_id)
    )
    stmt = include_deleted_records(stmt, Ping, include_deleted=False)

    pings = session.execute(stmt).scalars().all()
    if not pings:
        return False
    for ping in pings:
        ping.deleted_at = datetime.now(timezone.utc)
    return True


# ======================= SUPPORT =======================
def create_support_query(
    session: Session,
    user_id: int,
    email: str,
    messages: Dict[str, Any],
    query_type: str,
    is_urgent: bool = False
) -> Support:
    """
    Create and return a Support query record (uncommitted).

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user submitting the query.
        email (str): The email of the user.
        messages (Dict[str, Any]): The messages content.
        query_type (str): The type of query.
        is_urgent (bool): Whether the query is marked as urgent.

    Returns:
        Support: The newly created Support object.
    """
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
    """
    Fetch a Support query by ID, optionally including soft-deleted records.

    Args:
        session (Session): The database session.
        support_id (int): The ID of the support query.
        include_deleted (bool): Whether to include soft-deleted queries.

    Returns:
        Optional[Support]: The Support object if found, else None.
    """
    
    stmt = select(Support).where(Support.id == support_id)
    stmt = include_deleted_records(stmt, Support, include_deleted)

    result = session.execute(stmt)
    return result.scalar_one_or_none()


def update_support_query(
    session: Session, 
    support_id: int, 
    **kwargs
) -> Optional[Support]:
    """
    Update a Support query record and return it (uncommitted).

    Args:
        session (Session): The database session.
        support_id (int): The ID of the support query to update.
        **kwargs: Fields to update.

    Returns:
        Optional[Support]: The updated Support object if found, else None.
    """
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
    """
    Soft-delete a Support query by setting deleted_at.

    Args:
        session (Session): The database session.
        support_id (int): The ID of the support query to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    support = get_support_by_id(session, support_id, include_deleted=True)
    if not support:
        return False

    support.deleted_at = datetime.now(timezone.utc)
    return True