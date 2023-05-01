from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('static/token.json'):
        creds = Credentials.from_authorized_user_file('static/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'static/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('static/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        today = date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1) 
        tmax = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        timemax = tmax.isoformat() + 'Z'  
        events_result = service.events().list(calendarId='primary', timeMin=now,timeMax=timemax,
                                              maxResults=1, singleEvents=True,orderBy='startTime').execute()
        events = events_result.get('items', [])
        if events:
            googlejson = json.dumps(events[0]) 
            #print(googlejson)
            with open('static/google.json', 'w') as f:
                f.write(googlejson)
        else:
            googlejson = {
                'summary': 'no-event',
                'start': {
                    'dateTime': 'no-date'
                }
            }
            #print(googlejson)
            with open('static/google.json', 'w') as f:
                json.dump(googlejson, f)

        if not events:
            print('No upcoming events found.')
            return

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()

