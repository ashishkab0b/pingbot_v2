
from flask import current_app

from models import Ping

class MessageConstructor:
    """
    This class constructs the message and the URL for a ping.
    Specifically, it replaces variables in the message and URL with values from the database.
    """
    URL_VARIABLES = {
        "<PING_ID>": {
            "description": "The ID of the ping in the database.",
            "db_table": "pings",
            "db_column": "id",
        },
        "<REMINDER_TIME>": {
            "description": "The time at which the reminder will be sent.",
            "db_table": "pings",
            "db_column": "reminder_ts",
            "format_ts": True,
        },
        "<SCHEDULED_TIME>": {
            "description": "The time at which the ping is scheduled to be sent.",
            "db_table": "pings",
            "db_column": "scheduled_ts",
            "format_ts": True,
        },
        "<EXPIRE_TIME>": {
            "description": "The time at which the ping will expire.",
            "db_table": "pings",
            "db_column": "expire_ts",
            "format_ts": True,
        },
        "<DAY_NUM>": {
            "description": "The day number of the ping (Day 0 is date of participant signup).",
            "db_table": "pings",
            "db_column": "day_num",
        },
        "<PING_TEMPLATE_ID>": {
            "description": "The ID of the ping template in the database.",
            "db_table": "ping_templates",
            "db_column": "id",
        },
        "<PING_TEMPLATE_NAME>": {
            "description": "The name of the ping template.",
            "db_table": "ping_templates",
            "db_column": "name",
        },
        "<STUDY_ID>": {
            "description": "The ID of the study in the database.",
            "db_table": "studies",
            "db_column": "id",
        },
        "<STUDY_PUBLIC_NAME>": {
            "description": "The public name of the study.",
            "db_table": "studies",
            "db_column": "public_name",
        },
        "<STUDY_INTERNAL_NAME>": {
            "description": "The internal name of the study.",
            "db_table": "studies",
            "db_column": "internal_name",
        },
        "<STUDY_CONTACT_MSG>": {
            "description": "The contact message for the study.",
            "db_table": "studies",
            "db_column": "contact_message",
        },
        "<PID>": {
            "description": "The researcher-assigned participant ID.",
            "db_table": "enrollments",
            "db_column": "study_pid",
        },
        "<ENROLLMENT_ID>": {
            "description": "The ID of the enrollment in the database.",
            "db_table": "enrollments",
            "db_column": "id",
        },
        "<ENROLLMENT_SIGNUP_DATE>": {
            "description": "The date the participant enrolled in the study.",
            "db_table": "enrollments",
            "db_column": "signup_ts",
            "format_ts": True,
        },
        "<PR_COMPLETED>": {
            "description": "The proportion of completed pings out of sent pings (i.e., excluding future pings).",
            "db_table": "enrollments",
            "db_column": "pr_completed",
        },
    }

    MESSAGE_VARIABLES = URL_VARIABLES | {
        "<URL>": {
            "description": "The URL to include in the message.",
            "db_table": "ping_templates",
            "db_column": "url",
        },
    }
    
    def __init__(self, ping: Ping):
        """
        Initialize with the provided ping.
        """
        self.ping = ping
        self.telegram_id = self.ping.enrollment.telegram_id
        self.url = None
        self.survey_link = None
        self.message = None
        
    def format_ts(self, ts, tz):
        """
        Format a timestamp for display in a message with AM/PM.
        """
        return ts.astimezone(tz).strftime("%Y-%m-%d %I:%M:%S %p %Z")
        
    def construct_ping_link(self):
        """
        Construct an HTML link for the ping. 
        This is done at the point of sending the ping and is called by construct_message.
        """
        forwarding_code = self.ping.forwarding_code
        url = f"{current_app.config['BASE_URL']}/api/ping/{self.ping.id}?code={forwarding_code}"
        url_text = self.ping.ping_template.url_text if self.ping.ping_template.url_text else current_app.config['PING_DEFAULT_URL_TEXT']
        self.survey_link = f"<a href='{url}'>{url_text}</a>"
        
        return self.survey_link
        
    def construct_message(self):
        """
        Construct a message with a URL.
        This is done at the point of sending the ping and is called by the task that is sending the ping.
        """
        message = self.ping.ping_template.message
        survey_link = self.construct_ping_link() if self.ping.ping_template.url else None
        
        if "<URL>" in self.ping.ping_template.message:
            message = message.replace("<URL>", survey_link)
        elif survey_link:
            message += f"\n\n{survey_link}"
        
        for key, value in self.MESSAGE_VARIABLES.items():
            if value['db_table'] == 'pings':
                
                # Format the timestamp if necessary
                if "format_ts" in value and value["format_ts"]:
                    new_val = self.format_ts(getattr(self.ping, value['db_column']), self.ping.enrollment.tz)
                else: 
                    new_val = getattr(self.ping, value['db_column'])
                    
                # Replace the placeholder with the correct value
                message = message.replace(key, str(new_val))
                
            elif value['db_table'] == 'studies':
                
                # Format the timestamp if necessary
                if "format_ts" in value and value["format_ts"]:
                    new_val = self.format_ts(getattr(self.ping, value['db_column']), self.ping.enrollment.tz)
                else: 
                    new_val = getattr(self.ping, value['db_column'])
                    
                # Replace the placeholder with the correct value
                message = message.replace(key, str(new_val))
                
            elif value['db_table'] == 'ping_templates':
                
                # Format the timestamp if necessary
                if "format_ts" in value and value["format_ts"]:
                    new_val = self.format_ts(getattr(self.ping, value['db_column']), self.ping.enrollment.tz)
                else: 
                    new_val = getattr(self.ping, value['db_column'])
                    
                # Replace the placeholder with the correct value
                message = message.replace(key, str(new_val))
                
            elif value['db_table'] == 'enrollments':
                
                # Format the timestamp if necessary
                if "format_ts" in value and value["format_ts"]:
                    new_val = self.format_ts(getattr(self.ping, value['db_column']), self.ping.enrollment.tz)
                else: 
                    new_val = getattr(self.ping, value['db_column'])
                    
                # Replace the placeholder with the correct value
                message = message.replace(key, str(new_val))
                
        
        self.message = message
        return message
        
    def construct_survey_url(self):
        """
        Construct a URL for a ping. 
        This is done in the ping forwarding route at the point of redirecting to the survey after the participant clicks.
        """
        url = self.ping.ping_template.url

        for key, value in self.URL_VARIABLES.items():
            if value['db_table'] == 'pings':
                url = url.replace(key, str(getattr(self.ping, value['db_column'])))
            elif value['db_table'] == 'studies':
                url = url.replace(key, str(getattr(self.ping.enrollment.study, value['db_column'])))
            elif value['db_table'] == 'ping_templates':
                url = url.replace(key, str(getattr(self.ping.ping_template, value['db_column'])))
            elif value['db_table'] == 'enrollments':
                url = url.replace(key, str(getattr(self.ping.enrollment, value['db_column'])))
        
        self.url = url
        return url
    
    def construct_reminder(self):
        message = "Reminder:\n" + self.construct_message()
        self.message = message
        return message