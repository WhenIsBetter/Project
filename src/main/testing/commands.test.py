from spm_bot.DiscordBot import DiscordBot
from lib import FakeChannel

# Create a fake discord text channel to use for relaying fake messages to the bot
fake_channel = FakeChannel.FakeChannel()
# Create the bot object but do not login
bot = DiscordBot()
# Bind the on_message method to our fake channel
fake_channel.add_callback(bot.on_message)


class Colors:
    BLUE = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'


# Checks if two inputs are identical for testing, returns True if passed, false if failed
def expect(method_name, actual, expected):
    failed = actual != expected

    if failed:
        print(f"{Colors.RED}[{method_name}] Test failed! {Colors.RESET}Expected {Colors.BLUE}'{expected}'{Colors.RESET} but got {Colors.BLUE}'{actual}'{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[{method_name}] Test passed!{Colors.RESET} {Colors.BLUE}{actual} {Colors.RESET}== {Colors.BLUE}{expected}{Colors.RESET}")

    return not failed


# Test command for arguments in a command
async def test_ping_pong_command(_):

    # Trigger the bot to send a fake message back that says this: Pong!
    await fake_channel.send("!ping")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_ping_pong_command', fake_channel.messages[-1], "pong!")


# Test command for arguments in a command
async def test_args_test_command1(_):

    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']
    await fake_channel.send("!test akdl falkd f;alsd f;lkasdf")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_args_test_command1', fake_channel.messages[-1], "[TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']")


# Test command for arguments in a command
async def test_args_test_command2(_):

    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: []
    await fake_channel.send("!test")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_args_test_command2', fake_channel.messages[-1], "[TESTING ENV] Your args were: []")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    # Methods to run tests for
    tests = [
        test_ping_pong_command,
        test_args_test_command1,
        test_args_test_command2
    ]

    # Results of tests after they're ran, maps method -> boolean
    results = {}

    # Tests to run
    for test in tests:
        results[test] = loop.run_until_complete(test(loop))

    print("\n")
    successful = 0
    failed = 0
    for test, passed in results.items():
        if passed:
            successful += 1
        else:
            failed += 1

    print(f"==========================================\nTotal Discord Bot command tests ran: {len(results)}")
    print(f"Tests passed/failed: {successful}/{failed} ({round(successful / len(results) * 100)}%)")
    print("==========================================")

    loop.close()
