from datetime import timedelta
from math import floor
from discord import Message

from spm_bot.commands.AbstractCommand import AbstractCommand
from scheduler.EventScheduler import EventScheduler


# A simple command to test the use of arguments in a command
class ReportCommand(AbstractCommand):

    def __init__(self, bot, name: str, **kwargs):
        super().__init__(bot, name, **kwargs)

        self.main_arg = "report"
        self.missing_names = ["missing", "miss"]

        self.main_usage = f"{self.bot.command_prefix}{self.main_arg} <event ID> [missing (# or %)]"
        self.miss_usage = f"{self.missing_names[0]} <# or __% of people allowed to miss the event>"

        self.args_complaint = f"Report command: Bad arguments! Usage: {self.main_usage}"
        self.miss_complaint = f"Optional argument: Usage: {self.miss_usage}"
        self.numb_complaint = f"The number of people missing must be an integer between 0 and the number attending!"

    async def __get_db_call(self, id_):
        return await self.bot.database.get_event(id_)

    async def execute(self, message: Message, args: list):

        if not args:
            await message.channel.send(self.args_complaint)
            return

        id_ = args[0]
        event = None
        try:
            # event = await self.bot.database.get_event(id_)
            event = await self.__get_db_call(id_)
        except KeyError:
            event = None


        if not event:
            await message.channel.send(
                f"{message.author.mention} No event found with the ID `{id_}`. Please verify the ID and "
                f"try again.")
            return

        invited = len(event.attendees)
        allowed_missing = 0

        if len(args) > 1:
            if len(args) > 3 or args[1] not in self.missing_names:
                await message.channel.send(self.args_complaint)
                return

            try:
                if "%" in args[2]:
                    percent = int(args[2].strip("%"))
                    allowed_missing = int(percent * invited)
                else:
                    allowed_missing = int(args[2])
                if allowed_missing < 0 or allowed_missing >= invited:
                    raise ValueError()
                allowed_missing += 1 # some1 tell me y we need +1 here
            except ValueError:   # also catches if int() fails
                await message.channel.send(self.numb_complaint)
                return

        print_buffer  =  "### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###\n"
        print_buffer += event.start.strftime(f"Event {id_}: %a %d %b, %H:%M %p - ")
        print_buffer += event.end.strftime('%H:%M %p')
        if event.end.date() > event.start.date():
            print_buffer += event.end.strftime(' %m/%d')
        print_buffer += "\n\n"

        last_missing = 0
        print(event.__dict__)
        times = self.bot.scheduler.calc_times(event, max_missing=0)
        missing = 1
        temp_times = self.bot.scheduler.calc_times(event, max_missing=1)
        while(True):
            if missing > invited or len(list(filter(
                    lambda x: (x[0].start != x[1].start or x[0].end != x[1].end),
                    zip(temp_times, times)))) > 0:
                print_buffer += self.__convert_print(event, times, last_missing, missing)
                if missing >= allowed_missing:
                    break
                times = temp_times
                last_missing = missing
            missing += 1
            temp_times = self.bot.scheduler.calc_times(event, max_missing=missing)

        print_buffer += "### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###\n"
        await message.channel.send(print_buffer)
        return

    def __convert_print(self, event, times, last_missing, missing):
        if times is None:
            return ""
        buffer = ""

        range_text = f"{last_missing} to {missing - 1} people missing"
        if missing - last_missing == 1: # if it's <= 0 then something went drastically wrong
            range_text = f"up to {last_missing} people missing"
            if last_missing == 0:
                range_text = f"everyone present"
            elif last_missing == 1:
                range_text = f"up to 1 person missing"
        buffer += f" # Available times with {range_text}:\n"

        if len(times) == 0:
            buffer = f" # No available times with {range_text}:\n\n"
            return buffer

        include_empty_days = True   # could change to, eg, only if >= 33% of days have content
        i = 0
        start_date = event.start.date()
        while start_date <= event.end.date():
            day_result = ""
            while i < len(times) and times[i].start.date() == start_date:
                day_result += f" \t\t *  {times[i].start.strftime('%H:%M %p')} - {times[i].end.strftime('%H:%M %p')}"
                if times[i].end.date() > times[i].start.date():
                    day_result += times[i].end.strftime(' %m/%d')   # do we need to worry about multiple years?
                day_result += "\n"
                i += 1 # ...nah... as long as the *gap* is under a year, and that's firmly out of our specs
            if day_result != "" or include_empty_days:
                buffer += start_date.strftime(" \t - %a %d %b \n") + day_result
            start_date += timedelta(days=1)

        buffer += "\n"
        return buffer


