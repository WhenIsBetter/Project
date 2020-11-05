from spm_bot.DiscordBot import DiscordBot
from lib import FakeChannel

# Create a fake discord text channel to use for relaying fake messages to the bot
fake_channel = FakeChannel.FakeChannel()
# Create the bot object but do not login
bot = DiscordBot()
# Bind the on_message method to our fake channel
fake_channel.add_callback(bot.on_message)

# Test command for arguments in a command
async def test_ping_pong_command(loop):

    print("Performing test for !ping command...")
    # Trigger the bot to send a fake message back that says this: Pong!
    await fake_channel.send("!ping")
    # Make sure that the last message sent is the bot responding correctly
    assert fake_channel.messages[-1] == "pong!"
    print("Test successful!\n")

# Test command for arguments in a command
async def test_args_test_command1(loop):

    print("Performing test for !test command with arguments...")
    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']
    await fake_channel.send("!test akdl falkd f;alsd f;lkasdf")
    # Make sure that the last message sent is the bot responding correctly
    assert fake_channel.messages[-1] == "[TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']"
    print("Test successful!\n")

# Test command for arguments in a command
async def test_args_test_command2(loop):

    print("Performing test for !test command with no arguments...")
    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: []
    await fake_channel.send("!test")
    # Make sure that the last message sent is the bot responding correctly
    assert fake_channel.messages[-1] == "[TESTING ENV] Your args were: []"
    print("Test successful!\n")



if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    # Tests to run
    loop.run_until_complete(test_ping_pong_command(loop))
    loop.run_until_complete(test_args_test_command1(loop))
    loop.run_until_complete(test_args_test_command2(loop))

    loop.close()
