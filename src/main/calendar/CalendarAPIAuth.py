from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from pytz import utc
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
        '../../deploy/credentials.json', SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")


'''
save authentication code into database so it can be loaded as needed
'''
def save_auth_code(user, auth_code): # TODO implement
    pass


'''
load authentication code from database for a given discord user
returns: calendar api credentials for the given user in plaintext, returns None value if credentials are not found
'''
def load_auth_code(user): # TODO implement
    pass


'''
check if user is authenticated
returns a boolean value that is true if the user has an authentication code already stored
in the database, and false if the user does not have an authentication code stored
'''
def is_authenticated(user):
    return load_auth_code(user) is not None


# returns a string containing a url that a user uses to obtain their authorization code
def get_authorization_url():
    return flow.authorization_url()[0]


'''
get events for a given user between start_date and end_date

params:
start_time, end_time: datetime date in ISO format
user: discord user ID to request calendar events from

returns: next 10 events upcoming in the users calendar
'''
def get_events(user, start_date, end_date):
    flow.fetch_token(code=load_auth_code(user))  # update flow with the users credentials so it can create a token
    creds = flow.credentials  # create credentials for the current user
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API to get events between start_time and end_time
    print("getting events between {} and {}".format(start_date, end_date))
    events_result = service.events().list(calendarId='primary', timeMin=start_date,
                                          timeMax=end_date,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
