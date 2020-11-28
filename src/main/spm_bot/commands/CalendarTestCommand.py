from discord import Message

from src.main.calendar.CalendarAPIAuth import get_events
from spm_bot.commands.AbstractCommand import AbstractCommand
from datetime import datetime, timedelta
from pytz import utc


# simple command to test the functionality of the calendar API request
class CalendarTestCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):
        await message.channel.send("running calendar test!")
        print(message.author)

        start_date = datetime.now(utc).isoformat('T')
        end_date = (datetime.now(utc) + timedelta(days=5)).isoformat('T')
        get_events("nik", start_date, end_date)
