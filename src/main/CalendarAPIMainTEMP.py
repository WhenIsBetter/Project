from __future__ import print_function
import datetime
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#  this file is very temporary, it was purely created to demonstrate how to use the calendar API to grab events within a
#  range of time. This classes functionality will most likely be split into the EventScheduler and GoogleAccount classes

# these scopes are saved in the token.pickle, so if they are changed you must delete the token.pickle file
from pytz import utc

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


# calls the calendar api to retrieve all of the users events from monday 10/19 to friday 10/23
def get_events():
    # TODO: understand some of the auth magic so we can use a link to authorize through the discord bot
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../../deploy/calendar-API-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # call the calendar api
    print("getting events from 10/19-10/23")
    events_result = service.events().list(calendarId='primary', timeMin=datetime.now(utc).isoformat('T'),
                                          timeMax=(datetime.now(utc) + timedelta(days=5)).isoformat('T'), singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
