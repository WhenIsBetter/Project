import discord


# Represents an instance of the bot for one specific server
class DiscordBot:
    #  -- Public: --

    def __init__(self, token):
        # Misc. initializations go here:
        self.__scheduler = None
        self.token = token

        # Initialize variables related to the discord connection:
        self.client = discord.Client()
        self.on_message = self.client.event(self.on_message)  # register with explicit decorator call

    # Finish setting up the object with the scheduler
    def attach_scheduler(self, scheduler):
        self.__scheduler = scheduler
        # Tell the scheduler to initialize itself if it hasn't already

    @property
    def scheduler(self):
        if self.__scheduler is None:
            raise RuntimeError('Uninitialized Scheduler')
        return self.__scheduler

    # Return a list of DiscordUser objects -- from the UML diagram
    # FIXME: I've forgotten, why do we need this again?
    # I don't know why the bot itself needs to try and remember
    # an entire server's users. Was it because of caching, or something?
    def get_users(self):
        pass

    # -- Private: --

    # literally just pass on the run command
    def run(self, *args, **kwargs):
        self.client.run(self.token, *args, **kwargs)

    # Callback for messages. Should check if it's potentially a command
    #  and, if so, pass to _parse_command to check and delegate if so
    async def on_message(self, message):
        pass    # TODO

    # Internal function, taking a list of strings,
    #  that delegates command responses to an appropriate method
    def _parse_command(self, tokens):
        pass

    # TODO
    # functions like edit_response, new_event_response, etc.
    # they'll probably mostly pass stuff onto scheduler,
    # then send an appropriate message back to the server
