from discord import Message
import datetime

class FakeAuthor:
    def __init__(self):
        self.mention = "[TESTING ENV]"

class FakeMessage(Message):

    def __init__(self, content, fake_channel):
        self.content = content
        self.channel = fake_channel
        self.author = FakeAuthor()

    @property
    def created_at(self):
        """:class:`datetime.datetime`: The message's creation time in UTC."""
        return datetime.datetime.now()