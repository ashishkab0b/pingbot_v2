import random
import string
from math import ceil
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo  # Updated for zoneinfo
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

def random_time(
    signup_ts: datetime, 
    begin_day_num: int, 
    begin_time: str, 
    end_day_num: int, 
    end_time: str, 
    tz: str
) -> datetime:
    """
    Generate a random timestamp within a specified interval.

    Args:
        signup_ts (datetime): The signup timestamp (in UTC).
        begin_day_num (int): Start day offset from signup date.
        begin_time (str): Start time in 'HH:MM' format.
        end_day_num (int): End day offset from signup date.
        end_time (str): End time in 'HH:MM' format.
        tz (str): Timezone string (e.g., 'America/New_York').

    Returns:
        datetime: Random timestamp within the specified interval, adjusted for timezone.
    """
    timezone = ZoneInfo(tz)  # Updated for zoneinfo
    local_day_0 = signup_ts.astimezone(timezone).date()
    
    # Compute interval start and end dates
    interval_start_date = local_day_0 + timedelta(days=begin_day_num)
    interval_end_date = local_day_0 + timedelta(days=end_day_num)
    
    # Parse time strings
    begin_time_obj = datetime.strptime(begin_time, '%H:%M').time()
    end_time_obj = datetime.strptime(end_time, '%H:%M').time()
    
    # Combine dates and times into full datetime objects
    interval_start_ts = datetime.combine(interval_start_date, begin_time_obj, tzinfo=timezone)
    interval_end_ts = datetime.combine(interval_end_date, end_time_obj, tzinfo=timezone)
    
    # Ensure valid interval
    if interval_start_ts >= interval_end_ts:
        raise ValueError("The start of the interval must be before the end.")
    
    # Calculate a random time within the interval
    ping_interval_length = interval_end_ts - interval_start_ts
    random_seconds = randint(0, int(ping_interval_length.total_seconds()))
    ping_time = interval_start_ts + timedelta(seconds=random_seconds)
    
    return ping_time

def convert_dt_to_local(dt_obj, participant_tz):
    """
    Convert a datetime object to the participant's local time zone.
    """
    if not dt_obj or not participant_tz:
        return None

    try:
        # Ensure the datetime object has UTC timezone if tzinfo is missing
        if dt_obj.tzinfo is None:
            dt_obj = dt_obj.replace(tzinfo=timezone.utc)

        # Handle participant timezone
        participant_tz = participant_tz.strip()  # Remove extra spaces
        local_tz = ZoneInfo(participant_tz)  # Updated for zoneinfo
        
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

    # Get total count
    count_subquery = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(count_subquery)

    # Paginate
    offset = (page - 1) * per_page
    paginated_stmt = stmt.offset(offset).limit(per_page)
    results = session.execute(paginated_stmt)
    items = results.scalars().all()

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if per_page > 0 else 1

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages
    }