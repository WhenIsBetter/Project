from datetime import datetime

from discord import Message, Member, Embed, Color

from spm_bot.Event import Event
from spm_bot.commands.AbstractCommand import AbstractCommand

# Datetime parsing helpers
months = [None, "Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
num_suffix = ["th", "st", "nd", 'rd']

def get_num_suffix(num):
    if num > 3:
        return 'th'
    else:
        return num_suffix[num]


class DateFormatException(BaseException):
    ERROR_MESSAGE = 'date must be in the format of: `MM/DD/YYYY-HH:MM-(AM/PM)` ex. `11/6/2020-8:00-AM`'


class EventAdminCommand(AbstractCommand):

    def __init__(self, bot, name: str, **kwargs):
        super().__init__(bot, name, **kwargs)

        self.create_arg = 'create'
        self.modify_arg = 'modify'
        self.delete_arg = 'delete'

        # Just some user friendly stuff to spit back out when incorrect input is given
        self.base_usage = f"{self.bot.command_prefix}{self.name} < {self.create_arg} | {self.modify_arg} | {self.delete_arg} > [args...]"
        self.create_usage = f"{self.bot.command_prefix}{self.name} {self.create_arg} <start date> <end date>\n*Note: dates should be provided in the following format:*\n`MM/DD/YYYY-HH:MM-AM/PM`"
        self.modify_usage = f"{self.bot.command_prefix}{self.name} {self.modify_arg} <event ID> <new start date> <new end date>\n*Note: dates should be provided in the following format:*\n`MM/DD/YYYY-HH:MM-AM/PM`"
        self.delete_usage = f"{self.bot.command_prefix}{self.name} {self.delete_arg} <event ID> [confirm]"

    async def send_embed(self, channel, color=Color.green(), author=None, header=None, fields=None, footer=None):

        if fields is None:
            fields = [[]]
        emb = Embed(title=header, color=color)
        for field in fields:
            assert len(field) > 1

            if len(field) > 2:
                emb.add_field(name=field[0], value=field[1], inline=field[2])
            else:
                emb.add_field(name=field[0], value=field[1], inline=False)

        if author:
            emb.set_author(name=author)

        if footer:
            emb.set_footer(text=footer)

        await channel.send(embed=emb)

    # TODO: make role name a config option
    def is_event_admin(self, member: Member):

        # First check if the member is a server admin, default to true if they are
        if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
            return True

        # Now check their roles
        for role in member.roles:
            if role.name.upper() == 'EVENT ADMIN':
                return True

    async def execute(self, message: Message, args: list):

        # Only event admins can run this command
        if not self.is_event_admin(message.author):
            await self.send_embed(message.channel, color=Color.dark_red(),
                                  fields=[['Permission Denied!', f"Only users with the `Event Admin` role can use this command!", True]])
            return

        if not args:
            await self.send_embed(message.channel, color=Color.dark_red(), fields=[['Missing Arguments!', f"{self.base_usage}", True]])
            return

        subcommand = args[0]

        if subcommand.lower() not in (self.create_arg, self.modify_arg, self.delete_arg):
            await self.send_embed(message.channel, color=Color.dark_red(), fields=[['Invalid Subcommand!', f"{self.base_usage}", True]])
            return

        if subcommand.lower() == self.create_arg:
            await self._process_create_subcommand(message, args)
        elif subcommand.lower() == self.modify_arg:
            await self._process_modify_subcommand(message, args)
        elif subcommand.lower() == self.delete_arg:
            await self._process_delete_subcommand(message, args)

    # Can throw FormatException if given incorrectly
    @staticmethod
    async def parse_datetime(date_string: str) -> datetime:

        date_time_split: list = date_string.split('-', maxsplit=1)
        # Needs to be split between date and the time itself
        if len(date_time_split) != 2:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

        date, time = date_time_split  # Unpacks the list into variables

        date_split = date.split('/')
        if len(date_split) != 3:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

        mon, day, year = date_split

        time_am_pm_split: list = time.split('-')
        if len(time_am_pm_split) != 2:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

        actual_time, am_pm = time_am_pm_split

        hour_minute_split = actual_time.split(':')
        if len(hour_minute_split) != 2:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

        hour, minute = hour_minute_split

        # Now just make sure we have valid inputs
        try:
            mon = int(mon)
            day = int(day)
            year = int(year)
            hour = int(hour)
            minute = int(minute)

            if am_pm.upper() not in ("AM", "PM"):
                raise ValueError()
        except ValueError:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

        # some am/pm conversion
        # in the AM, midnight needs to be converted to hour 0
        if am_pm.upper() == 'AM' and hour == 12:
            hour = 0
        # In the pm if it's after noon we need to add 12 to the hour
        elif am_pm.upper() == 'PM' and hour != 12:
            hour += 12

        # If I'm understanding the datetime docs correctly, it seems that if something is out of bounds an
        # OverflowError is thrown, if this isn't the case then we will need to do more sanity checking
        try:
            return datetime(month=mon, day=day, year=year, hour=hour, minute=minute)
        except OverflowError:
            raise DateFormatException(DateFormatException.ERROR_MESSAGE)

    # Takes a datetime object and gives a clean representation of it
    @staticmethod
    async def clean_datetime(dt: datetime):

        actual_hour = dt.hour
        am_pm = "AM" if dt.hour < 12 else "PM"

        if actual_hour == 0:
            actual_hour = 12
        elif actual_hour > 12:
            actual_hour = actual_hour - 12

        actual_min = str(dt.minute)
        if dt.minute < 10:
            actual_min = f"0{actual_min}"


        return f"{months[dt.month]} {dt.day}{get_num_suffix(dt.day)}, {dt.year} at {actual_hour}:{actual_min}{am_pm}"

    async def _process_create_subcommand(self, message: Message, args: list):

        # Need the arg that invokes this subcommand, a start date, and end date at the least
        if len(args) < 3:
            await self.send_embed(message.channel, color=Color.red(), fields=[['Missing Arguments!', f"{self.create_usage}", True]])
            return

        start_date = args[1]  # Don't freak out, args[0] is 'create'
        end_date = args[2]

        start_datetime = None
        end_datetime = None

        try:
            start_datetime = await self.parse_datetime(start_date)
            end_datetime = await self.parse_datetime(end_date)
        except DateFormatException:
            await self.send_embed(message.channel, color=Color.red(),
                                  fields=[['Incorrect date format!', f"{DateFormatException.ERROR_MESSAGE}", True]])
            return

        if start_datetime > end_datetime:
            await self.send_embed(message.channel, color=Color.red(), fields=[["Invalid Dates!", "The start date must be before the end date!"]])
            return

        event = Event(start_datetime, end_datetime, message.author.id, message.guild.id)

        document = await self.bot.database.create_event(event)

        await self.send_embed(message.channel, color=Color.green(), header=f'Created the event: `{document["_id"]}`!',
                              fields=[['Starts', await self.clean_datetime(start_datetime), True], ['Ends', await self.clean_datetime(end_datetime), True]])

    async def _process_modify_subcommand(self, message: Message, args: list):

        if len(args) < 4:
            await self.send_embed(message.channel, color=Color.red(), fields=[['Missing Arguments!', f"{self.modify_usage}", True]])
            return

        id = args[1]
        event = await self.bot.database.get_event(id)
        if not event:
            await self.send_embed(message.channel, color=Color.red(),
                                  fields=[['No event found!', f"Please verify the ID `{id}` and try again.", True]])
            return

        start_date = args[2]
        end_date = args[3]

        try:
            start_datetime = await self.parse_datetime(start_date)
            end_datetime = await self.parse_datetime(end_date)
        except DateFormatException:
            await self.send_embed(message.channel, color=Color.red(),
                                  fields=[['Incorrect date format!', f"{DateFormatException.ERROR_MESSAGE}", True]])
            return

        if start_datetime > end_datetime:
            await self.send_embed(message.channel, color=Color.red(), fields=[["Invalid Dates!", "The start date must be before the end date!"]])
            return

        # Update the event in the db
        new_event = await self.bot.database.update_event(id, {'start': start_datetime,
                                                    'end': end_datetime})

        await self.send_embed(message.channel, color=Color.green(), header="Event Updated!",
                              fields=[["Event ID", f"`{id}`", True], ["Now Starts At", await self.clean_datetime(start_datetime), True], ["Now Ends At", await self.clean_datetime(end_datetime), True]])

    async def _process_delete_subcommand(self, message: Message, args: list):

        if len(args) < 2:
            await self.send_embed(message.channel, color=Color.red(), fields=[['Missing Arguments!', f"{self.delete_usage}", True]])
            return

        id = args[1]
        event = await self.bot.database.get_event(id)
        if not event:
            await self.send_embed(message.channel, color=Color.red(),
                                  fields=[['No event found!', f"Please verify the ID `{id}` and try again.", True]])
            return

        try:
            if args[2].upper() == 'CONFIRM':
                await self.bot.database.delete_event(id)
                await self.send_embed(message.channel, color=Color.green(),
                                      fields=[['Event Deleted!', f"Event with the ID: `{id}` has been deleted.", True]])
                return
        except IndexError:
            pass

        await self.send_embed(message.channel, color=Color.orange(), fields=[['Are you sure?', f"Are you sure you want to delete the event with the ID `{id}`?"]], footer=f"Please type `{self.bot.command_prefix}{self.name} {self.delete_arg} {id} CONFIRM` to proceed.")
