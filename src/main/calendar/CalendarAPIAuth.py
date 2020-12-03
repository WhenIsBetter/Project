from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from pytz import utc
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
        '../../deploy/credentials.json', SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")

'''
direct message a user over discord to get their calendar api token and store token
into database
'''
def authenticate_new_user(user):
    pass


'''
save token into database so it can be loaded as needed
'''
def save_token(user, token): # TODO implement
    pass


'''
load token from database for a given discord user
returns: calendar api credentials for the given user in plaintext, returns None value if credentials are not found
'''
def load_token(user): # TODO implement
    pass


'''
check if user is authenticated
returns a boolean value that is true if the user has a calendar api token already stored
in the database, and false if the user does not have a token stored
'''
def is_authenticated(user):
    return load_token(user) is not None


# returns a string containing a url that a user can use to obtain their calendar token
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
    oauth_code = load_token(user)
    flow.fetch_token(code=oauth_code)
    creds = flow.credentials
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
