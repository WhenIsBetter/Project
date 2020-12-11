from discord import Message

from spm_bot.commands.AbstractCommand import AbstractCommand
from datetime import datetime, timedelta
from pytz import utc

from src.main.calendar.CalendarAPIAuth import is_authenticated, get_authorization_url, get_events


# simple command to test the functionality of the calendar API request
class CalendarTestCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):

        await message.channel.send("running calendar test!")
        user = message.author
        user_id = message.author.id

        start_date = datetime.now(utc).isoformat('T')
        end_date = (datetime.now(utc) + timedelta(days=5)).isoformat('T')

        # if user not authenticated, send a direct message prompting them to authenticate
        if not (await is_authenticated(self.bot, user_id)):
            # get token from user over direct message
            user_dm_channel = await user.create_dm()
            await user_dm_channel.send("you need to authenticate with google calendar "
                                       "for this bot to be able to schedule events for you\n"
                                       "visit this url and paste the token returned to you into this chat: {}".format(get_authorization_url()))
            pass
        else:
            await get_events(self.bot, user_id, start_date, end_date)

