import random
import string
import math
from math import ceil
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
import pytz
from pytz import UTC
from random import randint

from typing import Dict, Any
from sqlalchemy.orm import Session

from flask import current_app
from extensions import db



def generate_non_confusable_code(length, lowercase, uppercase, digits):
    if not (lowercase or uppercase or digits):
        raise ValueError("At least one of lowercase, uppercase, or digits must be True.")
    # Define non-confusable characters
    non_confusable_chars = ''
    if lowercase:
        non_confusable_chars += ''.join(ch for ch in string.ascii_lowercase if ch not in {'l', 'o'})
    if uppercase:
        non_confusable_chars += ''.join(ch for ch in string.ascii_uppercase if ch not in {'I', 'O'})
    if digits:
        non_confusable_chars += ''.join(ch for ch in string.digits if ch not in {'0', '1'})
    return ''.join(random.choices(non_confusable_chars, k=length))


def random_time(signup_ts: datetime, begin_day_num: int, begin_time: str, end_day_num: int, end_time: str, tz: str) -> datetime:
    local_day_0 = signup_ts.astimezone(pytz.timezone(tz)).date()
    interval_start_date = local_day_0 + timedelta(days=begin_day_num)
    interval_end_date = local_day_0 + timedelta(days=end_day_num)
    begin_time = datetime.strptime(begin_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    tz = pytz.timezone(tz)
    interval_start_ts = datetime.combine(interval_start_date, begin_time, tzinfo=tz)
    interval_end_ts = datetime.combine(interval_end_date, end_time, tzinfo=tz)
    ping_interval_length = interval_end_ts - interval_start_ts
    ping_time = interval_start_ts + timedelta(seconds=randint(0, int(ping_interval_length.total_seconds())))
    return ping_time

# def convert_dt_to_local(dt_obj, participant_tz):
#     """
#     Convert a datetime object to the participant's local time zone.
#     """
#     # print(type(dt_obj))
#     # print(type(participant_tz))
#     print(dt_obj)
#     print(participant_tz)
    
#     if not dt_obj or not participant_tz:
#         return None
#     try:
#         if dt_obj.tzinfo is None:
#             dt_obj = dt_obj.replace(tzinfo=UTC)
        

#         if participant_tz in pytz.all_timezones:
#             local_tz = pytz.timezone(participant_tz)
#         else:
#             local_tz = timezone(participant_tz)
#         local_dt = dt_obj.astimezone(local_tz)
#         return local_dt
#     except Exception as e:
#         current_app.logger.warning(f"Error converting time with tz={participant_tz}: {e}")
#         return dt_obj
       

def convert_dt_to_local(dt_obj, participant_tz):
    """
    Convert a datetime object to the participant's local time zone.
    """
    if not dt_obj or not participant_tz:
        return None

    try:
        # Ensure the datetime object has UTC timezone if tzinfo is missing
        if dt_obj.tzinfo is None:
            dt_obj = dt_obj.replace(tzinfo=UTC)

        # Handle participant timezone
        participant_tz = participant_tz.strip()  # Remove extra spaces
        if participant_tz in pytz.all_timezones:
            local_tz = pytz.timezone(participant_tz)
        else:
            raise ValueError(f"Invalid timezone: {participant_tz}")
        
        # Convert to local timezone
        local_dt = dt_obj.astimezone(local_tz)
        return local_dt

    except Exception as e:
        # Log exception (replace `current_app.logger.warning` with print if not in Flask)
        print(f"Error converting time with tz={participant_tz}: {e}")
        return dt_obj

def paginate_statement(
    session: Session,
    stmt,
    page: int = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    """
    Given a SELECT statement and a session, return a dict with:
      - items: the rows from this page
      - page: current page
      - per_page: items per page
      - total: total count of rows
      - pages: total number of pages
    """

    # Get total count excluding soft deleted rows
    # count_subquery = stmt.with_only_columns(func.count()).order_by(None)
    count_subquery = (
        stmt.filter(stmt.selected_columns.deleted_at.is_(None))
        .with_only_columns(func.count())
        .order_by(None)
    )
    total = session.scalar(count_subquery)

    # Paginate
    offset = (page - 1) * per_page
    paginated_stmt = stmt.offset(offset).limit(per_page)
    results = session.execute(paginated_stmt)
    items = results.scalars().all()

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total else 1

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages
    }