from discord import Message

from src.main.spm_bot.commands.AbstractCommand import AbstractCommand
from src.main.scheduler.EventScheduler import EventScheduler


# A simple command to test the use of arguments in a command
class RecordCommand(AbstractCommand):

    def __init__(self, bot, name: str, **kwargs):
        super().__init__(bot, name, **kwargs)

        self.main_arg = "report"
        self.main_usage = f"{self.bot.command_prefix}{self.name} {self.main_arg} <event ID>"

    async def execute(self, message: Message, args: list):

        if not args:
            await message.channel.send(f"{message.author.mention} Missing arguments! Usage: {self.base_usage}")
            return

        id_ = args[0]
        event = self.bot.database.get_event(id_)

        if not event:
            await message.channel.send(
                f"{message.author.mention} No event found with the ID `{id}`. Please verify the ID and "
                f"try again.")
            return

        self.bot.scheduler.
