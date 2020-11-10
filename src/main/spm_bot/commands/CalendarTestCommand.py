from discord import Message

from src.main.calendar.CalendarAPIAuth import get_events
from spm_bot.commands.AbstractCommand import AbstractCommand


# simple command to test the functionality of the calendar API request
class CalendarTestCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):
        await message.channel.send("running calendar test!")
        get_events("nik")
