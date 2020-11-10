from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from _datetime import datetime, timedelta
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

'''
save token into database so it can be loaded as needed
'''
def save_token(user, token): # TODO implement
    pass


'''
load token from database for a given discord user
returns: calendar api credentials for the given user in plaintext BE CAREFUL WITH THIS
'''
def load_token(user): # TODO implement
    pass


'''
get events for a given user, if the user has no saved credentials in the database, prompt the user for their token
and then save it to the database
returns: next 10 events upcoming in the users calendar
'''
def get_events(user):  # TODO move this command to another file, this file should be for auth only
    flow = InstalledAppFlow.from_client_secrets_file(
        '../../../deploy/credentials.json', SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
    url, _ = flow.authorization_url()
    print("visit this url: {}".format(url))
    oauth_code = input("Paste your code here: ")
    flow.fetch_token(code=oauth_code)
    creds = flow.credentials
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
