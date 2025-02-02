# tasks.py


from datetime import datetime, timezone
from extensions import db
from celery_app import celery
from models import Ping, Enrollment
from telegram_messenger import TelegramMessenger
from flask import current_app
from message_constructor import MessageConstructor
from crud import get_pings_to_send, get_pings_for_reminder, get_pings_by_enrollment_id
from flask import jsonify

@celery.task
def check_and_send_pings():
    with current_app.app_context():
        session = db.session
        now = datetime.now(timezone.utc)

        # Query for pings that need to be sent and update sent_ts
        pings_to_send = get_pings_to_send(session, now)
        for ping in pings_to_send:
            ping.sent_ts = now
        session.commit()  # commit the updates

        if len(pings_to_send) == 0:
            return

        current_app.logger.info(f"Found {len(pings_to_send)} pings to send.")
        current_app.logger.debug(f"Found {len(pings_to_send)} pings to send: {[ping.id for ping in pings_to_send]}")

        # Initialize Telegram Messenger
        bot_token = current_app.config['TELEGRAM_SECRET_KEY']
        telegram_messenger = TelegramMessenger(bot_token)

        # Send the pings
        for ping in pings_to_send:
            enrollment = ping.enrollment
            telegram_id = enrollment.telegram_id

            if not telegram_id:
                current_app.logger.warning(f"No telegram_id for enrollment {enrollment.id}")
                continue

            msg_constructor = MessageConstructor(ping)
            message = msg_constructor.construct_message()

            success = telegram_messenger.send_ping(telegram_id, message)

            if success:
                current_app.logger.info(f"Ping {ping.id} sent to telegram_id {telegram_id}")
            else:
                current_app.logger.error(f"Failed to send ping {ping.id} to telegram_id {telegram_id}")
                ping.sent_ts = None
                session.commit()  # commit this individual reset

        # Update probability completed for enrollments.
        try:
            for ping in pings_to_send:
                all_pings = get_pings_by_enrollment_id(session, ping.enrollment_id)
                already_sent_pings = [p for p in all_pings if p.sent_ts is not None]
                completed_sent_pings = [p for p in already_sent_pings if p.first_clicked_ts is not None]
                pr_completed = len(completed_sent_pings) / len(already_sent_pings) if already_sent_pings else 0.0
                ping.enrollment.pr_completed = pr_completed
            session.commit()  # commit after updating all enrollments
        except Exception as e:
            current_app.logger.error("Failed to update pr completed in batch of enrollments.")
            current_app.logger.exception(e)
            return jsonify({"error": "Internal server error."}), 500

        # Now handle reminders
        check_and_send_reminders(session, telegram_messenger, now)

def check_and_send_reminders(session, telegram_messenger, now):
    # Query for pings that need a reminder and update reminder_sent_ts
    pings_for_reminder = get_pings_for_reminder(session, now)
    for ping in pings_for_reminder:
        ping.reminder_sent_ts = now
    session.commit()  # commit the reminder timestamps

    if len(pings_for_reminder) == 0:
        return

    current_app.logger.info(f"Found {len(pings_for_reminder)} pings to send reminders for.")
    current_app.logger.debug(f"Found {len(pings_for_reminder)} pings to send reminders for: {[ping.id for ping in pings_for_reminder]}")

    # Send the reminders
    for ping in pings_for_reminder:
        enrollment = ping.enrollment
        telegram_id = enrollment.telegram_id

        if not telegram_id:
            current_app.logger.warning(f"No telegram_id for enrollment {enrollment.id}")
            continue

        msg_constructor = MessageConstructor(ping)
        message = msg_constructor.construct_reminder()

        success = telegram_messenger.send_ping(telegram_id, message)

        if success:
            current_app.logger.info(f"Reminder for ping {ping.id} sent to telegram_id {telegram_id}")
        else:
            current_app.logger.error(f"Failed to send reminder for ping {ping.id} to telegram_id {telegram_id}")
            ping.reminder_sent_ts = None
            session.commit()