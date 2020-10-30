from discord import TextChannel

from src.tests.lib import FakeMessage


# Since our bot infrastructure depends on discord.py classes and their methods, we are going to spoof them by
# overriding any attributes and methods that will allow the bot to work in an internal testing environment while not
# relying on discord at all. Here we have a fake text channel, that simply just keeps track of messages that have
# sent and will trigger the bot to run code.
class FakeChannel(TextChannel):

    # Not ideal to override a constructor without a super() call but python lets us do it, so oh well
    def __init__(self):
        self.messages = []
        self.callbacks = []

    # Overrides the default TextChannel send() method, keep track of the message for later and trigger any bot's
    # callback that may be listening to this channel
    async def send(self, content=None, *, tts=False, embed=None, file=None,
                                          files=None, delete_after=None, nonce=None,
                                          allowed_mentions=None, **kwargs):
        self.messages.append(content)

        print(f"[Fake Discord Channel Incoming Message]: {content}")

        args = [FakeMessage.FakeMessage(content, self)]

        for callback in self.callbacks:
            await callback(*args)

    # Add a callback to be triggered from a message sending in this channel
    # cb parameter MUST be an unexecuted async method
    def add_callback(self, cb):
        self.callbacks.append(cb)
