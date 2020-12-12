from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
    '../../deploy/credentials.json', SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")

'''
check if user is authenticated
returns a boolean value that is true if the user has an authentication code already stored
in the database, and false if the user does not have an authentication code stored
'''
async def is_authenticated(bot, discord_user_id):
    return await bot.load_auth_code(discord_user_id) is not None


# returns a string containing a url that a user uses to obtain their authorization code
def get_authorization_url():
    return flow.authorization_url()[0]


'''
get events for a given user between start_date and end_date

params:
start_time, end_time: datetime date in ISO format
discord_user_id: discord user ID to request calendar events from

returns: next 10 events upcoming in the users calendar
'''
async def get_events(bot, discord_user_id, start_date, end_date):
    flow.fetch_token(code=await bot.load_auth_code(discord_user_id))  # update flow with the users credentials so it can create a token
    creds = flow.credentials  # create credentials for the current user
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API to get events between start_time and end_time
    # print("getting events between {} and {}".format(start_date, end_date))
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
