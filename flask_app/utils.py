import random
import string
import math
from math import ceil
from sqlalchemy import select, func
from datetime import datetime, timedelta
import pytz
from random import randint

from typing import Dict, Any
from sqlalchemy.orm import Session

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


def random_time(start_date: datetime, begin_day_num: int, begin_time: str, end_day_num: int, end_time: str, tz: str) -> datetime:
    interval_start_date = start_date + timedelta(days=begin_day_num)
    interval_end_date = start_date + timedelta(days=end_day_num)
    begin_time = datetime.strptime(begin_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    tz = pytz.timezone(tz)
    interval_start_ts = datetime.combine(interval_start_date, begin_time, tzinfo=tz)
    interval_end_ts = datetime.combine(interval_end_date, end_time, tzinfo=tz)
    ping_interval_length = interval_end_ts - interval_start_ts
    ping_time = interval_start_ts + timedelta(seconds=randint(0, int(ping_interval_length.total_seconds())))
    return ping_time
       

# def paginate_query(query, page=1, per_page=10):
#     # Remove ordering on the query to speed up count
#     count_q = query.with_entities(db.func.count()).order_by(None)
#     total = count_q.scalar() or 0

#     items = query.offset((page - 1) * per_page).limit(per_page).all()
#     pages = math.ceil(total / per_page) if per_page else 1

#     return {
#         "items": items,
#         "total": total,
#         "page": page,
#         "per_page": per_page,
#         "pages": pages
#     }
    

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
    count_subquery = stmt.with_only_columns(func.count()).order_by(None)
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