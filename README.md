# WhenIsBetter Discord Bot

A Discord bot used to schedule optimal meeting times for members of a Discord server. Finds acceptable times by comparing users’ Google Calendars.

## Dependencies
- `discord` A python framework designed for running Discord bots in Python.
- `motor` An asynchronous driver for MongoDB
- `google-api-python-client` 
- `google-auth-httplib`
- `google-auth-oauthlib` 
- `pytest` A python testing framework for running automated tests.

## Installation
- Install required packages using pip by running `pip install -r requirements.txt`
- Make a `token.txt` file contained in a directory named `deploy` containing your bot's Discord token.
- Run `src/main/main.py`
- Manual testing can be performed through src/main/test.py

## Testing
Testing instructions go here as well as listing pytest as a requirement (maybe the dpytest requirement should be listed in the requirements)