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

## Commands
Bot's default prefix is `!`, start a message with this character to invoke a command.
Some commands have aliases, making commands easier to type/remember.
- `!event <create | modify | delete>` Command to be used by event admins to manage events stored by the bot.

When using the `create` subcommand, A start and an end range timestamp must be provided as arguments. For example:
`!event create 11/6/2020-8:00-PM 11/6/2020-10:00-PM` creates an event from 8-10PM on 11/6.

When using the `modify` or `delete` subcommand, the event ID must be provided. Every event in the database has a unique ID.


## Testing
Testing instructions go here as well as listing pytest as a requirement (maybe the dpytest requirement should be listed in the requirements)