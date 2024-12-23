from crontab import CronTab
import requests
from datetime import datetime, timedelta, timezone

'''

This script is used to build a cron schedule for the messenger service. 

The script asks the API to query the database for all pings scheduled for the current day and then creates a schedule for the messenger service to send those pings at the appropriate time.

The script also ensures that it will be run at the beginning of each day to build the schedule for that day.

'''



def get_pings_for_date():
    ''' Query the database and return the pings for today '''
    # Log the start of the request
    current_app.logger.info("Received request to get pings for today.")
    
    # Get today's date
    today = datetime.now(timezone.utc).date()
    
    # Query the database for pings scheduled for today
    pings = Ping.query.filter(Ping.scheduled_ts >= today).filter(Ping.scheduled_ts < today + timedelta(days=1)).all()
    
    # Log the number of pings found
    current_app.logger.info(f"Found {len(pings)} pings for today.")
    
    return pings