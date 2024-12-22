from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key
from logger_setup import setup_logger
import os
import random
import uuid
import string
import pytz
from dotenv import load_dotenv
from utils import generate_non_confusable_code

logger = setup_logger()
load_dotenv()


class User():
    
    def __init__(self, table):
        self.table = table
        self.email = None
        self.firstname = None
        self.lastname = None
    
    def db_add_user(self, firstname, lastname, email, password_hash):
        
        self.table.put_item(
            Item={
                'PK': f'USER#{email}',
                'SK': f'USER#{email}',
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'password_hash': password_hash
            }
        )
        
    def load_user(self, email):
        response = self.table.get_item(
            Key={
                'PK': f'USER#{email}',
                'SK': f'USER#{email}'
            }
        )
        item = response['Item']
        if item is None:
            logger.error(f'User with email {email} not found')
            return None
        self.email = item['email']
        self.firstname = item['firstname']
        self.lastname = item['lastname']
        return self
    
    def db_delete_user(self):
        '''
        Delete user from db
        (USER#UserID, STUDY#StudyID) and (STUDY#StudyID, USER#UserID)
        '''
        self.table.delete_item(
            Key={
                'PK': f'USER#{self.email}',
                'SK': f'USER#{self.email}'
            }
        )
        
    
    def add_study(self, study_id):
        '''
        Add two entries to db: (USER#UserID, STUDY#StudyID) and (STUDY#StudyID, USER#UserID)
        '''
        self.table.put_item(
            Item={
                'PK': f'USER#{self.email}',
                'SK': f'STUDY#{study_id}'
            }
        )
        self.table.put_item(
            Item={
                'PK': f'STUDY#{study_id}',
                'SK': f'USER#{self.email}'
            }
        )
        

class Study():
    
    def __init__(self, table):
        
        self.table = table
        self.study_code_length = 8
        self.study_code
        self.name = None
        self.user_id = None
        self.study_id = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'user_id': self.user_id,
            'study_id': self.study_id,
            'study_code': self.study_code
        }

    # def generate_study_code(self):
    #     # Define non-confusable characters
    #     non_confusable_chars = ''.join(ch for ch in string.ascii_lowercase if ch not in {'l', 'o'})
    #     # Generate an 8-character code
    #     return ''.join(random.choices(non_confusable_chars, k=self.study_code_length))

    def new_study(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.study_code = generate_non_confusable_code(length=self.study_code_length)
        self.study_id = str(uuid.uuid4())
        self.db_add_study()
        return self
    
    def db_add_study(self):
        '''
        Add a study to the database
        (STUDY#StudyID, USER#UserID) and (STUDY#StudyID, STUDY#StudyID)
        '''
        # Study details
        self.table.put_item(
            Item={
                'PK': f'STUDY#{self.study_id}',
                'SK': f'STUDY#{self.study_id}',
                'GSI1PK': f'CODE#{self.study_code}',
                'GSI1SK': f'CODE#{self.study_code}',
                'name': self.name
            }
        )
        # Add study to user's studies
        self.table.put_item(
            Item={
                'PK': f'USER#{self.user_id}',
                'SK': f'STUDY#{self.study_id}'
            }
        )
        # Add user to study's users
        self.table.put_item(
            Item={
                'PK': f'STUDY#{self.study_id}',
                'SK': f'USER#{self.user_id}',
            }
        )
    
    def get_study_by_code(self, study_code):
        '''
        Get a study by its study code
        '''
        study = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq(f'CODE#{study_code}')
        )
        if study['Items']:
            item = study['Items'][0]
            self.name = item.get('name', None)
            self.study_id = item.get('study_id', None)
            return self
    
    # def get_study(self, study_id):
    #     '''
    #     Get a study from the database
    #     '''
    #     study = self.table.get_item(
    #         Key={
    #             'PK': f'STUDY#{study_id}',
    #             'SK': f'STUDY#{study_id}'
    #         }
    #     )
    #     item = study['Item']
    #     if item is None:
    #         logger.error(f'Study with id {study_id} not found')
    #         return None
    #     self.name = item.get('name', None)
    #     self.study_id = item.get('study_id', None)
    #     return self
    
    def db_delete_study(self):
        pass
    
    def add_user(self):
        '''
        Add a user to a study
        (STUDY#StudyID, USER#UserID)
        (USER#UserID, STUDY#StudyID)
        '''
        
    
    

    
class Participant():
    
    def __init__(self, table):
        self.table = table
        self.participant_id = None
        self.tz = None
        self.studies = None
    
    def update_tz(self, tz, **kwargs):
        assert 'participant_id' in kwargs or 'telegram_id' in kwargs, 'Participant ID or Telegram ID required'
        if 'participant_id' in kwargs:
            self.table.update_item(
                Key={
                    'PK': f'PARTICIPANT#{kwargs["participant_id"]}',
                    'SK': f'PARTICIPANT#{kwargs["participant_id"]}'
                },
                UpdateExpression='SET tz = :val1',
                ExpressionAttributeValues={
                    ':val1': tz
                }
            )
        elif 'telegram_id' in kwargs:
            self.table.update_item(
                IndexName='GSI1',
                Key={
                    'GSI1PK': f'TELEGRAM#{kwargs["telegram_id"]}',
                    'GSI1SK': f'TELEGRAM#{kwargs["telegram_id"]}'
                },
                UpdateExpression='SET tz = :val1',
                ExpressionAttributeValues={
                    ':val1': tz
                }
            )
        return self
    
    def get_participant(self, participant_id=None, telegram_id=None):
        if participant_id:
            response = self.table.get_item(
                Key={
                    'PK': f'PARTICIPANT#{participant_id}',
                    'SK': f'PARTICIPANT#{participant_id}'
                }
            )
            if 'Items' in response:
                return response['Items'][0]
            return None
        elif telegram_id:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'TELEGRAM#{telegram_id}')
            )
            if 'Items' in response:
                return response['Items'][0]
            return None
    
    def get_tz(self, telegram_id=None, participant_id=None):
        if telegram_id:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'TELEGRAM#{telegram_id}')
            )
            if 'Items' in response and 'tz' in response['Items'][0]:
                return response['Items'][0]['tz']
            return None
        elif participant_id:
            response = self.table.get_item(
                Key={
                    'PK': f'PARTICIPANT#{participant_id}',
                    'SK': f'PARTICIPANT#{participant_id}'
                }
            )
            if 'Items' in response and 'tz' in response['Items'][0]:
                return response['Items'][0]['tz']
            return None
            
        
    def load_participant_studies(self, participant_id):
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'PARTICIPANT#{participant_id}') & Key('SK').begins_with('STUDY#')
        )
        if response['Items']:
            self.studies = [item['SK'].split('#')[1] for item in response['Items']]
        return self
    
    def new_participant(self, tz):
        assert tz in pytz.all_timezones, 'Invalid timezone'
        self.participant_id = str(uuid.uuid4())
        self.tz = tz
        self.db_add_participant()
        return self
    
    def enroll_participant(self, study_id, study_pid):
        '''
        - create study/participant and participant/study entries in db
        - get all ping templates for study
        - generate pings for each ping template and add them to db
        '''
        self.db_enroll_participant(self.participant_id, study_id, study_pid)
        ping_templates = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'STUDY#{study_id}') & Key('SK').begins_with('PINGTEMPLATE#')
        )
        # If no ping templates found, log and return
        if not ping_templates['Items']:
            logger.info(f'No ping templates found for study {study_id}')
            return 
        for item in ping_templates['Items']:
            ping_template_id = item['SK'].split('#')[1]
            ping_template = PingTemplate(self.table)
            ping_template.load_template(study_id, ping_template_id) # NOT DONE - START HERE
            pings = ping_template.generate_pings(
                participant_id=self.participant_id,
                study_pid=study_pid
                ) 
        
    def db_add_participant(self):
        '''
        Add a participant to the database without any studies
        (PARTICIPANT#PartID, PARTICIPANT#PartID): [tz]
        '''
        self.table.put_item(
            Item={
                'PK': f'PARTICIPANT#{self.participant_id}',
                'SK': f'PARTICIPANT#{self.participant_id}',
                'tz': self.tz,
                'created_at': datetime.now().isoformat()
            }
        )
    
    def db_enroll_participant(self, participant_id, study_id, study_pid):

        self.table.put_item(
            Item={
                'PK': f'STUDY#{study_id}',
                'SK': f'PARTICIPANT#{participant_id}',
                'study_pid': study_pid,
                'created_at': datetime.now().isoformat()
            }
        )
        self.table.put_item(
            Item={
                'PK': f'PARTICIPANT#{participant_id}',
                'SK': f'STUDY#{study_id}',
                'study_pid': study_pid,
                'created_at': datetime.now().isoformat()
            }
        )
    
    def db_delete_participant(self):
        '''
        Delete a participant from the database
        (STUDY#StudyID, PARTICIPANT#PartID)
        (PARTICIPANT#PartID, STUDY#StudyID)
        (PARTICIPANT#PartID, PARTICIPANT#PartID)
        '''
        pass
        

    
class PingTemplate():
    
    def __init__(self, table):
        
        self.table = table
        self.study_id = None
        self.ping_template_id = None
        self.ping_template_name = None
        
        self.message = None
        self.url = None
        self.reminder_latency = None
        self.expire_latency = None
        self.start_day_num = None
        self.schedule = None  # list of dicts e.g., [{'day_num': 0, 'start_time': '08:00', 'end_time': '10:00'}, ...]
        self.ping_df = None  # DataFrame of pings generated from the schedule
        
    def new_ping_template(self, study_id, 
                          ping_template_name, 
                          message, 
                          url, 
                          reminder_latency, 
                          expire_latency, 
                          schedule, 
                          start_day_num,
                          ):
        '''
        Create a ping template
        '''
        self.study_id = study_id
        self.ping_template_id = str(uuid.uuid4())
        self.ping_template_name = ping_template_name
        self.message = message
        self.url = url
        self.reminder_latency = reminder_latency
        self.expire_latency = expire_latency
        self.schedule = schedule
        self.start_day_num = start_day_num
        self.db_add_ping_template()
        return self
    
    def db_add_ping_template(self):
        '''
        Add a ping template to the database
        '''
        self.table.put_item(
            Item={
                'PK': f'STUDY#{self.study_id}',
                'SK': f'PINGTEMPLATE#{self.ping_template_id}',
                'study_id': self.study_id,
                'ping_template_id': self.ping_template_id,
                'ping_template_name': self.ping_template_name,
                'message': self.message,
                'url': self.url,
                'reminder_latency': self.reminder_latency,
                'expire_latency': self.expire_latency,
                'start_day_num': self.start_day_num,
                'schedule': self.schedule
            }
        )
        
    
    def db_delete_ping_template(self):
        '''
        Delete a ping template from the database
        '''
        self.table.delete_item(
            Key={
                'PK': f'PINGTEMPLATE#{self.ping_template_id}',
                'SK': f'PINGTEMPLATE#{self.ping_template_id}'
            }
        )
        logger.info(f'Deleted ping template with id {self.ping_template_id}')
        
    
    def load_template(self, study_id, ping_template_id):
        '''
        Get a ping template from the database
        '''
        ping_template = self.table.get_item(
            Key={
                'PK': f'STUDY#{study_id}',
                'SK': f'PINGTEMPLATE#{ping_template_id}'
            }
        )
        item = ping_template['Item']
        if item is None:
            logger.error(f'Ping template with id {ping_template_id} not found')
            return None
        self.study_id = item.get('study_id', None)
        self.ping_template_id = item.get('ping_template_id', None)
        self.ping_template_name = item.get('ping_template_name', None)
        self.message = item.get('message', None)
        self.url = item.get('url', None)
        self.reminder_latency = item.get('reminder_latency', None)
        self.expire_latency = item.get('expire_latency', None)
        self.schedule = item.get('schedule', None)
        return self
    
        
    
    
    def generate_pings(self, participant_id=None, study_pid=None):
        '''
        Given the schedule, generate pings at random times within the start and end times for each ping
        '''
        assert self.schedule is not None, 'Schedule is not set'
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        sched = pd.DataFrame(self.schedule)
        sched['date'] = today + timedelta(days=self.start_day_num + sched['day_num'])
        sched['start_ts'] = pd.to_datetime(sched['date'].astype(str) + ' ' + sched['start_time'])
        sched['end_ts'] = pd.to_datetime(sched['date'].astype(str) + ' ' + sched['end_time'])
        sched['duration'] = sched['end_ts'] - sched['start_ts']
        random_delta = pd.Series([pd.Timedelta(seconds=x.total_seconds()*np.random.rand()) for x in sched['duration']])
        sched['scheduled_ts'] = sched['start_time'] + random_delta
        self.ping_df = sched
        pings = []
        for i, row in sched.iterrows():
            ping = Ping(self.table)
            ping = ping.new_ping(
                study_id=self.study_id,
                participant_id=participant_id,
                study_pid=study_pid,
                ping_template_id=self.ping_template_id,
                ping_template_name=self.ping_template_name,
                scheduled_ts=row['scheduled_ts'],
                message=self.message,
                url=self.url,
                day_num=row['day_num'],
                reminder_latency=self.reminder_latency,
                expire_latency=self.expire_latency
            )
            pings.append(ping)
        return pings
            
    
class Ping():
    
    def __init__(self, table
                #  study_id: str, 
                #  participant_id: str, 
                #  ping_template_id: str, 
                #  ping_template_name: str, 
                # scheduled_ts: datetime,
                # message: str,
                # url: str,
                # day_num: int
                ):
        
        self.table = table
        self.study_id = None
        self.participant_id = None
        self.study_pid = None
        self.ping_template_id = None
        self.ping_template_name = None
        self.scheduled_ts = None
        self.message = None
        self.url = None
        self.day_num = None
        self.ping_id = None  
        self.sent_ts = None
        self.reminder_ts = None
        self.reminder_sent_ts = None
        self.expire_ts = None
        self.completed_ts = None
        self.enrolled = 1
        
    
    def new_ping(self, 
                 study_id, 
                 participant_id, 
                 study_pid,
                 ping_template_id, 
                 ping_template_name, 
                 scheduled_ts, 
                 message, 
                 url, 
                 day_num, 
                 reminder_latency=None,
                 expire_latency=None,
                 enrolled=1):

        self.study_id = study_id
        self.participant_id = participant_id
        self.study_pid = study_pid
        self.ping_template_id = ping_template_id
        self.ping_template_name = ping_template_name
        self.scheduled_ts = scheduled_ts
        self.message = message
        self.url = url
        self.day_num = day_num
        self.ping_id = str(uuid.uuid4())
        if reminder_latency:
            self.reminder_ts = scheduled_ts + timedelta(minutes=reminder_latency)
        if expire_latency:
            self.expire_ts = scheduled_ts + timedelta(minutes=expire_latency)
        self.db_add_ping()
        return self
        
    
    def db_add_ping(self):
        self.table.put_item(
            Item={
                'PK': f'PARTICIPANT#{self.participant_id}',
                'SK': f'PING#{self.ping_id}',
                'study_id': self.study_id,
                'participant_id': self.participant_id,
                'study_pid': self.study_pid,
                'ping_template_id': self.ping_template_id,
                'ping_template_name': self.ping_template_name,
                'scheduled_ts': self.scheduled_ts,
                'message': self.message,
                'url': self.url,
                'day_num': self.day_num,
                'reminder_ts': self.reminder_ts,
                'expire_ts': self.expire_ts
            }
        )
        
    def db_update_ping_sent(self, participant_id, ping_id, sent_ts):
        self.table.update_item(
            Key={
                'PK': f'PARTICIPANT#{participant_id}',
                'SK': f'PING#{ping_id}'
            },
            UpdateExpression='SET sent_ts = :val1',
            ExpressionAttributeValues={
                ':val1': sent_ts
            }
        )
    
    def db_update_ping_reminded(self, participant_id, ping_id, reminder_sent_ts):
        self.table.update_item(
            Key={
                'PK': f'PARTICIPANT#{participant_id}',
                'SK': f'PING#{ping_id}'
            },
            UpdateExpression='SET reminder_sent_ts = :val1',
            ExpressionAttributeValues={
                ':val1': reminder_sent_ts
            }
        )
        
    
    def db_delete_ping(self):
        self.table.delete_item(
            Key={
                'PK': f'PARTICIPANT#{self.participant_id}',
                'SK': f'PING#{self.ping_id}'
            }
        )
        
    def db_delete_pings_by_study(self):
        """
        Delete all pings for a study using BatchWriteItem
        """
        # Query the table to get all pings for the study
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'STUDY#{self.study_id}') & Key('SK').begins_with('PING#')
        )

        # Collect all items to delete
        items_to_delete = response.get('Items', [])
        
        # Check for additional pages of results
        while 'LastEvaluatedKey' in response:
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq(f'STUDY#{self.study_id}') & Key('SK').begins_with('PING#'),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response.get('Items', []))

        # Delete items in batches of 25
        for i in range(0, len(items_to_delete), 25):
            batch = items_to_delete[i:i + 25]
            with self.table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
    
    def db_delete_pings_by_participant(self):
        '''
        Delete all pings for a participant using BatchWriteItem
        '''
        # Query the table to get all pings for the participant
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'PARTICIPANT#{self.participant_id}') & Key('SK').begins_with('PING#')
        )
        
        # Collect all items to delete
        items_to_delete = response.get('Items', [])
        
        # Check for additional pages of results
        while 'LastEvaluatedKey' in response:
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq(f'PARTICIPANT#{self.participant_id}') & Key('SK').begins_with('PING#'),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response.get('Items', []))
            
        # Delete items in batches of 25
        for i in range(0, len(items_to_delete), 25):
            batch = items_to_delete[i:i + 25]
            with self.table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
                    
    def db_delete_pings_by_ping_template(self):
        '''
        Delete all pings for a ping template using BatchWriteItem
        '''
        # Query the table to get all pings for the ping template
        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression=Key('GSI2PK').eq(f'PINGTEMPLATE#{self.ping_template_id}') & Key('GSI2SK').begins_with('PING#')
        )
        
        # Collect all items to delete
        items_to_delete = response.get('Items', [])
        
        # Check for additional pages of results
        while 'LastEvaluatedKey' in response:
            response = self.table.query(
                IndexName='GSI2',
                KeyConditionExpression=Key('GSI2PK').eq(f'PINGTEMPLATE#{self.ping_template_id}') & Key('GSI2SK').begins_with('PING#'),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response.get('Items', []))
            
        # Delete items in batches of 25
        for i in range(0, len(items_to_delete), 25):
            batch = items_to_delete[i:i + 25]
            with self.table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
                    
        
        
    
    




