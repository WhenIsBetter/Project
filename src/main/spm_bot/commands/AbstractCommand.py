from discord import Message


# Commands will be stored as a map on the DiscordBot class that will map command names to their respective command
# instances that extend this class
class AbstractCommand:

    # All commands will use this constructor, where bot is the DiscordBot object in charge of this command,
    # name is what a discord user would put after a command prefix and aliases are optional alternative ways to call
    # the command in discord. i.e. if this command were to have a name of 'test', '!test' would cause the command to
    # execute. If we added aliases of 't' and 'te' to a command instance, we could also call the command with '!t'
    # and '!te'
    def __init__(self, bot, name: str, aliases=None):

        self.bot = bot
        self.name = name

        # If a list wasn't supplied or weren't given a list, default to no aliases
        if not isinstance(aliases, list):
            self.aliases: set = set()
        else:
            self.aliases: set = set(aliases)

    # This method should be overridden in a custom implementation of a command, this is code that runs when a user
    # executes the command. The original message object associated with this command is the message parameter,
    # and the arguments the user provides will be provided as a list of strings cleanly parsed from the message.
    async def execute(self, message: Message, args: list):
        raise NotImplementedError("Please extend this class and override this method!")

    # Returns the name of this command defined in the constructor.
    def get_name(self) -> str:
        return self.name

    # Returns the list of alternative names/identifiers that this command can also be called by.
    def get_aliases(self) -> set:
        return self.aliases
