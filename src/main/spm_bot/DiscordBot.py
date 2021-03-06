from datetime import datetime, timedelta

import discord


# Represents an instance of the bot for one specific server
from discord import Message, DMChannel

from database.Database import Database
from spm_bot.Event import Event
from scheduler.EventScheduler import EventScheduler
from scheduler.TimeRange import TimeRange
from database.MockDatabase import MockDatabase
from spm_bot.commands.ArgsTestCommand import ArgsTestCommand
from spm_bot.commands.EventAdminCommand import EventAdminCommand
from spm_bot.commands.PingPongCommand import PingPongCommand
from spm_bot.commands.CalendarTestCommand import CalendarTestCommand
from spm_bot.commands.AbstractCommand import AbstractCommand
from spm_bot.commands.ReportCommand import ReportCommand


class DiscordBot:
    #  -- Public: --

    def __init__(self, fake_database=False):
        # Misc. initializations go here:
        self.__scheduler = None   #   None

        # Initialize variables related to the discord connection:
        self.client = discord.Client()
        self.on_message = self.client.event(self.on_message)  # register with explicit decorator call

        # Initialize the database, fake_database param is used in tests, can also use while implementing features
        if fake_database:
            self.__database = MockDatabase()
        else:
            self.__database = Database()

        # Initialize things relating to commands, it will be a map that links a string identifier to a command instance
        self.command_prefix = "!"  # What should a message start with to identify it as a command?
        self.__commands = {}

        self.attach_scheduler(EventScheduler())

        # TODO Register actual commands here, these are simply here to show the system in action, remove them later
        self.register_command(PingPongCommand(self, 'ping', aliases=['pingpong', 'pongping']))
        self.register_command(ArgsTestCommand(self, 'test'))
        self.register_command(EventAdminCommand(self, 'event'))
        self.register_command(CalendarTestCommand(self, 'calendar', aliases=['calendartest', 'testcalendar']))
        self.register_command(ReportCommand(self, 'report'))

    # Finish setting up the object with the scheduler
    def attach_scheduler(self, scheduler):
        self.__scheduler = scheduler
        # Tell the scheduler to initialize itself if it hasn't already

    @property
    def scheduler(self):
        if self.__scheduler is None:
            raise RuntimeError('Uninitialized Scheduler')
        return self.__scheduler

    @property
    def database(self):
        return self.__database

    # Return a list of DiscordUser objects -- from the UML diagram
    # FIXME: I've forgotten, why do we need this again?
    # I don't know why the bot itself needs to try and remember
    # an entire server's users. Was it because of caching, or something?
    def get_users(self):
        pass

    # -- Private: --

    # literally just pass on the run command
    def run(self, token, *args, **kwargs):
        self.client.run(token, *args, **kwargs)

    # Registers a command that the discord bot should listen for and execute, a command we register should extend
    # AbstractCommand. If a command with a conflicting name exists, an error will be thrown.
    def register_command(self, command_instance: AbstractCommand):

        # Commands can't have similar identifiers/names
        if command_instance.get_name() in self.__commands:
            raise RuntimeError(f"Command/Alias with a name/identifier of {command_instance.get_name()} already exists!")

        # Add the command to the map so we can grab the instance later
        self.__commands[command_instance.get_name()] = command_instance

        # Our commands can also have aliases, in which we just map an alternate string to the same exact instance.
        for alias in command_instance.get_aliases():
            if alias in self.__commands:
                raise RuntimeError(f"Command/Alias with a name/identifier of {command_instance.get_name()} already exists!")

        # We are good to add all of the aliases to the map as well
        for alias in command_instance.get_aliases():
            self.__commands[alias] = command_instance

        print(f"[Commands] successfully registered the '{command_instance.get_name()}' command!")

    # Callback for messages. Should check if it's potentially a command
    #  and, if so, pass to _parse_command to check and delegate if so
    async def on_message(self, message: Message):

        # Happens when nothing is in the message, can happen with embeds, pictures, etc
        if not message.content:
            return

        # Is the message a direct message? If so pass it on to _parse_dm, also verify that the bot is not parsing
        # it's own messages so we don't infinite loop
        if isinstance(message.channel, DMChannel) and message.author.id != self.client.user.id:
            await self._parse_dm(message)
        # Does the message start with our prefix? If so parse it and handle it
        elif message.content.startswith(self.command_prefix):
            await self._parse_command(message)

    # Internal function, taking a discord message object,
    #  that handles the contents of a direct message to the bot
    async def _parse_dm(self, message: Message):
        # TODO check if dm is an auth code, we currently are assuming any dm's sent to the bot are auth codes
        await self.save_auth_code(message.author.id, message.content)  # store token in database

        # TEMPORARY, this reply is just used to verify that this method works
        # await message.channel.send("--dm read--\nauthor: {}\ncontent: {}".format(message.author.id, message.content))



    # Internal function, taking a discord message object,
    #  that delegates command responses to an appropriate method
    async def _parse_command(self, message: Message):

        # Split up the message by whitespace
        split_message = message.content.split(" ")
        # We know that the command is in the first index and that the prefix is contained
        command_name = split_message[0].replace(self.command_prefix, '', 1)  # Get first word in message, remove prefix

        # Is the command name something that is registered? If not, we can abort, TODO perhaps in the future we tell
        # the user that an invalid command was input?
        command_instance: AbstractCommand = self.__commands.get(command_name.lower())
        if not command_instance:
            return

        # We are now good to execute the command, args are the words separated by whitespace. If just a command was
        # provided without args, we will have an empty list.
        print(f"[Commands] ({message.created_at}) {message.author} used command: '{command_instance.get_name()}'")
        await command_instance.execute(message, split_message[1:])

    # save authentication code into database so it can be loaded as needed
    async def save_auth_code(self, discord_user_id, auth_code):  # TODO implement
        # temporary print to test that the method runs correctly
        # print("-----\n"
        #    "save_auth_code received code\n"
        #    "user id: {}\n"
        #    "code: {}\n"
        #    "-----".format(discord_user_id, auth_code))
        await self.__database.add_calendar_creds(discord_user_id, auth_code)

        pass

    # load authentication code from database for a given discord user id
    # returns: calendarapi credentials for user in plaintext, returns None value if credentials are not found
    async def load_auth_code(self, discord_user_id):  # TODO implement
        auth_code = await self.__database.get_calendar_creds(discord_user_id)
        # print("auth code loaded for user {}\ncode: {}".format(discord_user_id, auth_code))
        return auth_code


    # TODO
    # functions like edit_response, new_event_response, etc.
    # they'll probably mostly pass stuff onto scheduler,
    # then send an appropriate message back to the server
