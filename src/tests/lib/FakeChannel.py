from discord import TextChannel

from src.tests.lib import FakeMessage


class FakeChannel(TextChannel):

    def __init__(self):
        self.messages = []
        self.callbacks = []

    async def send(self, content=None, *, tts=False, embed=None, file=None,
                                          files=None, delete_after=None, nonce=None,
                                          allowed_mentions=None, **kwargs):
        self.messages.append(content)

        print(f"[Fake Discord Channel Incoming Message]: {content}")

        args = [FakeMessage.FakeMessage(content, self)]

        for callback in self.callbacks:
            await callback(*args)

    def add_callback(self, cb):
        self.callbacks.append(cb)

