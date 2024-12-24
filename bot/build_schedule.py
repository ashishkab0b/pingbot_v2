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
    url = f"{config.FLASK_APP_BOT_BASE_URL}/get_pings_in_time_interval"
    header = {"X-Bot-Secret-Key": config.BOT_SECRET_KEY}
    payload = {"start_ts": now.isoformat(), "end_ts": last_ts.isoformat()}
    response = requests.get(url, json=payload, headers=header)
    
    # Log errors
    if not response.ok:
        logger.error(f"Error getting pings for today: {response.status_code} {response.text}")
        return
    
    # Parse response
    try:
        pings = response.json()  # Attempt to parse JSON
    except ValueError:
        logger.error(f"Response is not valid JSON: {response.text}")
        return

    logger.info(f"Received {len(pings)} pings for date today ({today}).")
    logger.debug(f"Pings received: {[(x['id'], x['scheduled_ts']) for x in pings]}")
    return pings


def schedule_cron_jobs(pings: list):
    try:
        # Get the absolute path of the current script
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        send_ping_script = os.path.join(current_dir, 'send_ping_request.py')

        # Log the start of scheduling
        logger.info("Starting to schedule cron jobs.")

        cron = CronTab(user=True)
        
        # Remove existing jobs
        cron.remove_all()
        logger.info("Removed all existing cron jobs.")

        # Add new jobs
        success_count = 0
        fail_count = 0
        for ping in pings:
            try:
                # Convert ping.scheduled_ts to a cron-compatible schedule
                scheduled_time = datetime.fromisoformat(ping["scheduled_ts"])
                cron_time = scheduled_time.strftime("%M %H %d %m *")  # Minute, Hour, Day, Month, Any weekday

                # Create a new cron job
                job = cron.new(command=f'python3 {send_ping_script} {ping["id"]}')
                job.setall(cron_time)
                logger.info(f"Scheduled job for ping ID {ping['id']} at {scheduled_time}.")
                
            except Exception as e:
                logger.error(f"Error scheduling ping ID {ping['id']}.")
                logger.exception(e)
                fail_count += 1
            else:
                success_count += 1
        cron.write()            
        logger.info(f"Successfully wrote {success_count} jobs to crontab with {fail_count} errors.")


        # Add a job to run this script at the beginning of each day
        try:
            job = cron.new(command=f'python3 {current_file}')
            job.setall('0 0 * * *')
            cron.write()
        except Exception as e:
            logger.error("Error scheduling daily job.")
            logger.exception(e)
        else:
            logger.info("Scheduled daily job to run at 00:00.")


    except Exception as e:
        logger.error(f"An error occurred while scheduling cron jobs.")
        logger.exception(e)




if __name__ == '__main__':

    # Get pings for today
    pings = get_pings_for_schedule()
    
    # Schedule cron jobs
    if pings:
        schedule_cron_jobs(pings)
    else:
        logger.info("No pings to schedule.")