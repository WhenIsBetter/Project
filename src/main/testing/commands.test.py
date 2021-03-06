from lib.FakeMessage import FakeAuthor
from spm_bot.DiscordBot import DiscordBot
from lib import FakeChannel

# Create a fake discord text channel to use for relaying fake messages to the bot
from spm_bot.commands.EventAdminCommand import EventAdminCommand

fake_channel = FakeChannel.FakeChannel()
# Create the bot object but do not login
bot = DiscordBot(fake_database=True)
# Bind the on_message method to our fake channel
fake_channel.add_callback(bot.on_message)

# Fake authors used for when we need to override permissions and stuff
no_permission_author = FakeAuthor(administrator=False, manage_server=False)
event_admin_author = FakeAuthor(administrator=True, manage_server=True)

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


# Checks to make sure an input is not None, used mainly for database operations
def exists(method_name, var_name, input):
    failed = input is None

    if failed:
        print(f"{Colors.RED}[{method_name}] Test failed! {Colors.RESET}Expected {Colors.BLUE}'{var_name}'{Colors.RESET} to exist!")
    else:
        print(f"{Colors.GREEN}[{method_name}] Test passed!{Colors.RESET} {Colors.BLUE}{var_name} {Colors.RESET} exists!")

    return not failed


# Test command for arguments in a command
async def test_ping_pong_command(_):

    # Trigger the bot to send a fake message back that says this: Pong!
    await fake_channel.send("!ping")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_ping_pong_command', fake_channel.messages[-1].content, "pong!")


# Test command for arguments in a command
async def test_args_test_command1(_):

    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']
    await fake_channel.send("!test akdl falkd f;alsd f;lkasdf")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_args_test_command1', fake_channel.messages[-1].content, "[TESTING ENV] Your args were: ['akdl', 'falkd', 'f;alsd', 'f;lkasdf']")


# Test command for arguments in a command
async def test_args_test_command2(_):

    # Trigger the bot to send a fake message back that says this: [TESTING ENV] Your args were: []
    await fake_channel.send("!test")
    # Make sure that the last message sent is the bot responding correctly
    return expect('test_args_test_command2', fake_channel.messages[-1].content, "[TESTING ENV] Your args were: []")


# Test command for creating an event, and retrieving it
async def create_get_event_command(_):

    # Tell the bot to create an event at a certain time
    await fake_channel.send('!event create 11/6/2020-8:00-PM 11/6/2020-10:00-PM', author=event_admin_author)

    # We have to get the id generated in the message, its surrounded by graves
    start_index = fake_channel.messages[-1].embeds[0].title.find('`')
    id = fake_channel.messages[-1].embeds[0].title[start_index+1:start_index+9]
    # Now let's see if the event exists in the db
    event = await bot.database.get_event(id)

    return exists('create_get_event_command', 'event', event)

# Test command for creating an event, and deleting it without confirming the deletion
async def create_attempt_delete_event_command(_):

    # Tell the bot to create an event at a certain time
    await fake_channel.send('!event create 11/6/2020-8:00-PM 11/6/2020-10:00-PM', author=event_admin_author)

    # We have to get the id generated in the message, its surrounded by graves
    start_index = fake_channel.messages[-1].embeds[0].title.find('`')
    id = fake_channel.messages[-1].embeds[0].title[start_index+1:start_index+9]

    # Make sure the event exists
    if not await bot.database.get_event(id):
        return exists('create_attempt_delete_event_command', 'bot.database.get_event(id)', await bot.database.get_event(id))

    await fake_channel.send(f'!event delete {id}')

    # Should still exist
    return exists('create_attempt_delete_event_command', 'bot.database.get_event(id)', await bot.database.get_event(id))

# Test command for creating an event, and deleting it
async def create_delete_event_command(_):

    # Tell the bot to create an event at a certain time
    await fake_channel.send('!event create 11/6/2020-8:00-PM 11/6/2020-10:00-PM', author=event_admin_author)

    # We have to get the id generated in the message, its surrounded by graves
    start_index = fake_channel.messages[-1].embeds[0].title.find('`')
    id = fake_channel.messages[-1].embeds[0].title[start_index+1:start_index+9]

    # Make sure the event exists
    if not await bot.database.get_event(id):
        return exists('create_delete_event_command', 'bot.database.get_event(id)', await bot.database.get_event(id))

    await fake_channel.send(f'!event delete {id} CONFIRM', author=event_admin_author)

    # Should be none
    return expect('create_delete_event_command', await bot.database.get_event(id), None)


# Test command for making sure members w/o perms can't use the admin command
async def permission_admin_event_command(_):

    # Fake author without permissions
    await fake_channel.send('!event', author=no_permission_author)
    return expect('permission_admin_event_command', fake_channel.messages[-1].embeds[0].fields[0].name, 'Permission Denied!')


# Test command to see if replacing a timeframe for an event works
async def modify_event_command(_):

    # Create an event
    await fake_channel.send("!event create 12/6/2020-2:00-PM 12/6/2020-6:00-PM", author=event_admin_author)
    start_index = fake_channel.messages[-1].embeds[0].title.find('`')
    id = fake_channel.messages[-1].embeds[0].title[start_index+1:start_index+9]
    # Make sure the event exists
    if not await bot.database.get_event(id):
        return exists('create_delete_event_command', 'bot.database.get_event(id)', await bot.database.get_event(id))

    new_start = '12/20/2020-2:00-PM'
    new_end = '12/24/2020-2:00-PM'
    # Now update the timeframe
    await fake_channel.send(f"!event modify {id} {new_start} {new_end}", author=event_admin_author)

    # Verify that we have equal datetimes
    new_start_dt = await EventAdminCommand.parse_datetime(new_start)
    new_end_dt = await EventAdminCommand.parse_datetime(new_end)
    event = await bot.database.get_event(id)
    return expect('modify_event_command', [event.start, event.end], [new_start_dt, new_end_dt])

if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    # Methods to run tests for
    tests = [
        test_ping_pong_command,
        test_args_test_command1,
        test_args_test_command2,
        create_get_event_command,
        create_attempt_delete_event_command,
        create_delete_event_command,
        permission_admin_event_command,
        modify_event_command
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
