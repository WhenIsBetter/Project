from datetime import datetime

from scheduler.TimeRange import TimeRange
from spm_bot.DiscordBot import DiscordBot
from lib import FakeChannel
from spm_bot.Event import Event
from spm_bot.commands.ReportCommand import ReportCommand
#


# Create a fake discord text channel to use for relaying fake messages to the bot
fake_channel = FakeChannel.FakeChannel()
# Create the bot object but do not login
bot = DiscordBot()
# Bind the on_message method to our fake channel
fake_channel.add_callback(bot.on_message)

def expect(actual, expected):
    if actual != expected:
        print(f"\033[93m ERROR: Actual was >{actual}<, expected was >{expected}< \033[0m")
        raise AssertionError()

def __bad_testing():
    abcdEvent = Event(datetime.fromisoformat("2020-10-30 04:00"), datetime.fromisoformat("2020-10-30 05:30"))
    abcdEvent.attendees = [ None ]
    bot.scheduler.add_event(abcdEvent)

    morning_event = [None, None, None]
    for i in range(3):
        morning_event[i] = Event(datetime.fromisoformat("2020-12-04 07:15"), datetime.fromisoformat("2020-12-04 11:45"))
        morning_event[i].attendees = [ None, None, None ]
        bot.scheduler.add_event(morning_event[i])
        bot.scheduler.overlay_availability(morning_event[i], TimeRange(datetime.fromisoformat("2020-12-04 08:30"), datetime.fromisoformat("2020-12-04 10:30")))
        bot.scheduler.overlay_availability(morning_event[i], TimeRange(datetime.fromisoformat("2020-12-04 08:30"), datetime.fromisoformat("2020-12-04 10:30")))
        bot.scheduler.overlay_availability(morning_event[i], TimeRange(datetime.fromisoformat("2020-12-04 10:50"), datetime.fromisoformat("2020-12-04 11:25")))
        bot.scheduler.overlay_availability(morning_event[i], TimeRange(datetime.fromisoformat("2020-12-04 10:50"), datetime.fromisoformat("2020-12-04 11:25")))
    bot.scheduler.overlay_availability(morning_event[0], TimeRange(datetime.fromisoformat("2020-12-04 07:45"), datetime.fromisoformat("2020-12-04 08:15")))
    bot.scheduler.overlay_availability(morning_event[1], TimeRange(datetime.fromisoformat("2020-12-04 07:45"), datetime.fromisoformat("2020-12-04 08:30")))
    bot.scheduler.overlay_availability(morning_event[2], TimeRange(datetime.fromisoformat("2020-12-04 07:45"), datetime.fromisoformat("2020-12-04 08:45")))

    nameToEventDict = {
        'abcd': abcdEvent,
        'm1': morning_event[0],
        'm2': morning_event[1],
        'm3': morning_event[2]
    }
    return nameToEventDict

# Monkey-patch so it doesn't try to use the actual database
__nameToEventDict = __bad_testing()
async def __get_db_call(self, id_):
    return __nameToEventDict[id_]
__report_Com = bot._DiscordBot__commands["report"]
__report_Com._ReportCommand__get_db_call = __get_db_call.__get__(__report_Com, ReportCommand)

# Test default reply
async def test_report_fail(loop):
    await fake_channel.send("!report")
    expect( fake_channel.messages[-1].content, "Report command: Bad arguments! Usage: !report <event ID> [missing (# or %)]")


# Test other bad commands
async def test_miss_fail(loop):
    await fake_channel.send("!report abcd ishkamilligheeallakazatzkeeumpetybumptylaoooooh")
    expect( fake_channel.messages[-1].content, "Report command: Bad arguments! Usage: !report <event ID> [missing (# or %)]")
    await fake_channel.send("!report abcd missing 2 missing")
    expect( fake_channel.messages[-1].content, "Report command: Bad arguments! Usage: !report <event ID> [missing (# or %)]")

# Test report with basic example
async def test_report_basic(loop):
    await fake_channel.send("!report abcd")
    expected_result = '''### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
Event abcd: Fri 30 Oct, 04:00 AM - 05:30 AM

 # Available times with 0 to 1 people missing:
 	 - Fri 30 Oct 
 		 *  04:00 AM - 05:30 AM

### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
'''
    expect(fake_channel.messages[-1].content, expected_result)
    await fake_channel.send("!report abcd missing 0")
    expect( fake_channel.messages[-1].content, expected_result)
    await fake_channel.send("!report abcd miss 0")
    expect( fake_channel.messages[-1].content, expected_result)

# test with bad missing param
async def test_report_miss(loop):
    bad_msg = "The number of people missing must be an integer between 0 and the number attending!"
    await fake_channel.send("!report abcd missing 1")
    expect(fake_channel.messages[-1].content, bad_msg )
    await fake_channel.send("!report abcd missing -1")
    expect(fake_channel.messages[-1].content, bad_msg )
    await fake_channel.send("!report abcd miss 100%")
    expect(fake_channel.messages[-1].content, bad_msg )


# test with more real call
async def test_report_comp(loop):
    await fake_channel.send("!report m1 missing 2")
    expect(fake_channel.messages[-1].content, '''### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
Event m1: Fri 04 Dec, 07:15 AM - 11:45 AM

 # Available times with everyone present:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 07:45 AM
 		 *  08:15 AM - 08:30 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with up to 1 person missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 08:30 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with 2 to 3 people missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 11:45 AM

### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
''')
    await fake_channel.send("!report m2 missing 2")
    expect(fake_channel.messages[-1].content, '''### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
Event m2: Fri 04 Dec, 07:15 AM - 11:45 AM

 # Available times with everyone present:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 07:45 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with up to 1 person missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 08:30 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with 2 to 3 people missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 11:45 AM

### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
''')
    await fake_channel.send("!report m3 missing 2")
    expect(fake_channel.messages[-1].content, '''### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
Event m3: Fri 04 Dec, 07:15 AM - 11:45 AM

 # Available times with everyone present:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 07:45 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with up to 1 person missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 08:30 AM
 		 *  10:30 AM - 10:50 AM
 		 *  11:25 AM - 11:45 AM

 # Available times with up to 2 people missing:
 	 - Fri 04 Dec 
 		 *  07:15 AM - 08:30 AM
 		 *  08:45 AM - 11:45 AM

### +-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+ ###
''')

if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    # Tests to run
    loop.run_until_complete(test_report_fail(loop))
    loop.run_until_complete(test_miss_fail(loop))
    loop.run_until_complete(test_report_basic(loop))
    loop.run_until_complete(test_report_miss(loop))
    loop.run_until_complete(test_report_comp(loop))

    loop.close()
