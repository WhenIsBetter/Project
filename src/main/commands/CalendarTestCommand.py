from discord import Message

from commands.AbstractCommand import AbstractCommand


from calendar.CalendarAPIAuth import get_events


# simple command to test the functionality of the calendar API request
class CalendarTestCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):
        await message.channel.send("running calendar test!")
        get_events("nik")
