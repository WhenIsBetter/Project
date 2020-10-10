from discord import Message

from commands.AbstractCommand import AbstractCommand


# A simple command to test the use of arguments in a command
class ArgsTestCommand(AbstractCommand):

    async def execute(self, message: Message, args: list):
        await message.channel.send(f"{message.author.mention} Your args were: {args}")
