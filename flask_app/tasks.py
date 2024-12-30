# tasks.py


from datetime import datetime, timezone
from extensions import db
from celery_app import celery
from models import Ping, Enrollment
from telegram_messenger import TelegramMessenger
from flask import current_app
from blueprints.enrollments import MessageConstructor
from crud import get_pings_to_send, get_pings_for_reminder

@celery.task
def check_and_send_pings():
    """
    Periodic task to check and send pings that are scheduled to be sent.
    """
    with current_app.app_context():
        session = db.session
        now = datetime.now(timezone.utc)

        # Query for pings that need to be sent
        pings_to_send = get_pings_to_send(session, now)

        # Initialize Telegram Messenger
        bot_token = current_app.config['TELEGRAM_SECRET_KEY']
        telegram_messenger = TelegramMessenger(bot_token)

        for ping in pings_to_send:
            enrollment = ping.enrollment
            telegram_id = enrollment.telegram_id

            if not telegram_id:
                # Log and skip
                current_app.logger.warning(f"No telegram_id for enrollment {enrollment.id}")
                continue

            # Build the message
            msg_constructor = MessageConstructor(ping)
            message = msg_constructor.construct_message()

            # Send the message
            success = telegram_messenger.send_ping(telegram_id, message)

            if success:
                # Update sent_ts to now
                ping.sent_ts = now
                session.commit()
                current_app.logger.info(f"Ping {ping.id} sent to telegram_id {telegram_id}")
            else:
                # Log failure
                current_app.logger.error(f"Failed to send ping {ping.id} to telegram_id {telegram_id}")

        # Now handle reminders
        check_and_send_reminders(session, telegram_messenger, now)

def check_and_send_reminders(session, telegram_messenger, now):
    # Query for pings that need a reminder sent
    pings_for_reminder = get_pings_for_reminder(session, now)

    for ping in pings_for_reminder:
        enrollment = ping.enrollment
        telegram_id = enrollment.telegram_id

        if not telegram_id:
            current_app.logger.warning(f"No telegram_id for enrollment {enrollment.id}")
            continue

        # Build the reminder message
        msg_constructor = MessageConstructor(ping)
        message = msg_constructor.construct_reminder()

        # Send the reminder
        success = telegram_messenger.send_ping(telegram_id, message)

        if success:
            ping.reminder_sent = True
            ping.reminder_sent_ts = now
            session.commit()
            current_app.logger.info(f"Reminder for ping {ping.id} sent to telegram_id {telegram_id}")
        else:
            current_app.logger.error(f"Failed to send reminder for ping {ping.id} to telegram_id {telegram_id}")