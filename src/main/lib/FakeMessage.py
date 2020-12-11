from discord import Message
import datetime

# Since the bot uses an author object for debug purposes, we need something that the bot can read attributes from
class FakeAuthor:



    # In the codebase so far we only mention authors so this can be filled in as more attributes from message authors
    # are needed
    def __init__(self, administrator=False, manage_server=False):

        # Kinda gross, but this is needed for permission checking, add on necessary permissions as needed for testing
        class GuildPermissions:
            def __init__(self, administrator=False, manage_guild=False):
                self.administrator = administrator
                self.manage_guild = manage_guild

        self.mention = "[TESTING ENV]"
        self.id = 1717660517
        self.guild_permissions = GuildPermissions(administrator, manage_server)
        self.roles = []


# Our command framework forces discord.Message objects as parameters throughout the codebase
class FakeMessage(Message):

    # content - The contents of the message
    # fake_channel - The FakeChannel that this message was sent in
    def __init__(self, content, fake_channel, author=None):
        self.content = content
        self.channel = fake_channel

        if author:
            self.author = author
        else:
            self.author = FakeAuthor()

    # Similarly to the FakeAuthor class, our debug information uses message timestamps, so just override to something
    # we can use internally
    @property
    def created_at(self):
        """:class:`datetime.datetime`: The message's creation time in UTC."""
        return datetime.datetime.now()
