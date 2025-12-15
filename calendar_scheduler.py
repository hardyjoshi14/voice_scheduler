import logging
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        self.creds = Credentials.from_service_account_file(
            'service_account.json',
            scopes=self.SCOPES
        )
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def create_event(self, data:dict):
        """Create a calendar event"""
        try:
            start_time = datetime.fromisoformat(f"{data['date']}T{data['time']}")
            end_time = start_time + timedelta(hours=1)

            event = {
                'summary': data.get('title', 'Meeting'),
                'description': f"Scheduled with {data['name']}",
                'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
                'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
            }

            logger.info(f"Creating event: {event['summary']}")
            
            created_event = self.service.events().insert(
                calendarId='200c381b5325a04e286aca01ee48e02233316fb1131b5a6e03486fb33793fb98@group.calendar.google.com',
                body=event
            ).execute()

            return {
                'id': created_event.get('id'),
                'link': created_event.get('htmlLink', ''),
                'summary': created_event.get('summary', ''),
                'start': created_event.get('start', {}).get('dateTime', '')
            }
            
        except Exception as e:
            logger.error(f"Calendar error: {type(e).__name__}: {str(e)}")
            raise