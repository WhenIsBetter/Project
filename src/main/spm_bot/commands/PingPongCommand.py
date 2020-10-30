from discord import Message

from spm_bot.commands.AbstractCommand import AbstractCommand


# A simple command to demonstrate how to set up a command instance that extends the AbstractCommand class
class PingPongCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):
        await message.channel.send("pong!")
