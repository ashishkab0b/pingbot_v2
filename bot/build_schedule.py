from crontab import CronTab
from config import Config
import os
import requests
from datetime import datetime, timedelta, timezone
from logger_setup import setup_logger


'''
This script is used to build a cron schedule for the messenger service. 

The script asks the API to query the database for all pings scheduled for the current day and then creates a schedule for the messenger service to send those pings at the appropriate time.

The script also ensures that it will be run at the beginning of each day to build the schedule for that day.
'''

# Setup logging
logger = setup_logger()


# Load configuration
config = Config()


def get_pings_for_schedule():
    ''' Query the database and return upcoming pings'''
    
    # Log the start of the request
    logger.info("Querying pings to build today's schedule.")
    
    # Get today's date
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)
    # Get last possible timestamp within today's calendar date
    last_ts = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)
    
    # Query the database for pings scheduled for today
    url = f"{config.FLASK_APP_BOT_BASE_URL}/pings_for_date"
    header = {"X-Bot-Secret-Key": config.BOT_SECRET_KEY}
    payload = {"start_ts": now.isoformat(), "end_ts": last_ts.isoformat()}
    response = requests.get(url, json=payload, headers=header)
    
    # Log errors
    if not response.ok:
        logger.error(f"Error getting pings for today: {response.status_code} {response.text}")
        return
    
    # Parse response
    try:
        data = response.json()  # Attempt to parse JSON
    except ValueError:
        logger.error(f"Response is not valid JSON: {response.text}")
        return

    logger.info(f"Received {len(data)} pings for date today ({today}).")
    logger.debug(f"Pings received: {[(x['id'], x['scheduled_ts']) for x in data]}")
    return data["pings"]


def schedule_cron_jobs():
    try:
        # Retrieve pings for scheduling
        pings = get_pings_for_schedule()

        # Get the absolute path of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        send_ping_script = os.path.join(current_dir, 'send_ping_request.py')

        # Log the start of scheduling
        logger.info("Starting to schedule cron jobs.")

        with CronTab(user=True) as cron:
            # Remove existing jobs
            cron.remove_all()
            logger.info("Removed all existing cron jobs.")

            # Add new jobs
            for ping in pings:
                try:
                    # Convert ping.scheduled_ts to a cron-compatible schedule
                    scheduled_time = ping.scheduled_ts  # Assuming this is a datetime object
                    cron_time = scheduled_time.strftime("%M %H %d %m *")  # Minute, Hour, Day, Month, Any weekday

                    # Create a new cron job
                    job = cron.new(command=f'python3 {send_ping_script} {ping.id}')
                    job.setall(cron_time)
                    logger.info(f"Scheduled job for ping ID {ping.id} at {scheduled_time}.")
                    
                except Exception as e:
                    logger.error(f"Error scheduling ping ID {ping.id}.")
                    logger.exception(e)

            # Write all jobs to the crontab
            cron.write()
            logger.info("Successfully wrote jobs to crontab.")

    except Exception as e:
        logger.error(f"An error occurred while scheduling cron jobs.")
        logger.exception(e)




if __name__ == '__main__':
    
    pings = get_pings_for_schedule()
    schedule_cron_jobs()