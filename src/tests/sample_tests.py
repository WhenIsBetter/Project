import multiprocessing
import time
import traceback

import datetime

from src.main.Event import Event
from src.main.EventScheduler import EventScheduler
from src.main.TimeRange import TimeRange

from src.main.DiscordBot import DiscordBot

__tests = []

# Convenience method for testing -- print colored error on disparity
def expect(actual, expected):
    if actual != expected:
        print(f"\033[93m ERROR: Actual was >{actual}<, expected was >{expected}< \033[0m")

# decorator -- attach to normal test functions
def ptest(test, message = None):
    if message is None:
        message  = test.__name__
    global __tests
    __tests.append([test, message])
    return test

# decorator factory -- call prior to a test function that wouldn't return on its own
def busy_ptest_f(delay = 2.0, message = None):
    def wrapper(test):
        def proc():
            p = multiprocessing.Process(target=test, name=message, args=())
            p.start()
            time.sleep(delay)
            p.terminate()
            p.join()
        ptest(proc, message)
        return test
    return wrapper

# ----

@busy_ptest_f(delay=0.5)
def testBot():
    TOKEN = open("../../deploy/token.txt", "r").read()
    bot = DiscordBot(TOKEN)
    print(f"Logged in and ready to go!")
    bot.run()

@ptest
def testTimeRange():
    # note to self: ALWAYS use datetime.datetime.today(), not datetime.date.today(). You'll use a date, not a datetime.
    #  seems obvious when you write it out like that...
    tr = TimeRange(datetime.datetime(year=1959, month=2, day=3, hour=12, minute=57), datetime.datetime.today())
    print(f"The Day The Music Died: {tr.start}")
    print(f"Now: {tr.end}")
    print(f"How much time has passed: {tr.size}")

@ptest
def linkedlist_checks():
    ll = EventScheduler._List()
    expect( ll.empty(), True )

    # Ordering testing scenario

    starting_date = datetime.datetime.fromisoformat("2020-10-30 04:09:46.015638")
    node1 = EventScheduler._Node(starting_date - datetime.timedelta(days=5) )
    node8 = EventScheduler._Node(starting_date - datetime.timedelta(days=1) )
    node2 = EventScheduler._Node(starting_date - datetime.timedelta(days=1) )
    node3 = EventScheduler._Node(starting_date - datetime.timedelta(days=8) )
    node4 = EventScheduler._Node(starting_date - datetime.timedelta(days=11) )
    node5 = EventScheduler._Node(starting_date - datetime.timedelta(days=12) )
    node6 = EventScheduler._Node(starting_date - datetime.timedelta(days=7) )
    node7 = EventScheduler._Node(starting_date - datetime.timedelta(hours=12) )

    ll.insert(node1)
    expect(ll.empty(), False )

    ll.insert(node2)
    ll.insert(node3)
    ll.insert(node4)
    ll.insert(node5)
    ll.insert(node6)
    ll.insert(node7)
    ll.insert(node8)

    ll.delete(node3)

    # Check for correct output ordering -- we might run into floating-point errors, hence the delta

    expected_out = [ "2020-10-18 04:09:46.015646", "2020-10-19 04:09:46.015643", "2020-10-23 04:09:46.015648", "2020-10-25 04:09:46.015617", "2020-10-29 04:09:46.015635", "2020-10-29 04:09:46.015638", "2020-10-29 16:09:46.015651" ]

    i = 0
    el = ll.first.next
    while el is not ll.last:
        expect(el.key - datetime.datetime.fromisoformat(expected_out[i]) < datetime.timedelta(seconds=0.001), True )
        el = el.next
        i += 1

@ptest
def event_test():
     ES = EventScheduler()
     ev = Event(datetime.datetime(year=1959, month=2, day=3, hour=12, minute=57), datetime.datetime.today())
     ev2 = Event(datetime.datetime(year=1953, month=1, day=8, hour=0, minute=0, second=8), datetime.datetime.today())

     # check it correctly errors on an unregistered event

     try:
         ES._check_registered_event(ev)
         expect(0,1)
     except Exception:
         pass

    # add event testing -- check it registers alright

     ES.add_event(ev)

     expect(ES._check_registered_event(ev) is not None, True)

    # check it correctly errors on an unregistered event

     try:
         ES._check_registered_event(ev2)
         expect(0,1)
     except Exception:
         pass

     ES.add_event(ev2)

    # check get_events

     for (i,j) in zip(ES.get_events(), [ev, ev2]):
         expect(i, j)


def testing_scenario1(a, b):
    now = datetime.datetime.today()

    def CD(hours):  # 'current date' -- convenience function here
        return now + datetime.timedelta(hours=hours)

    ev = Event(CD(a), CD(b))

    ES = EventScheduler()
    ES.add_event(ev)

    # Try one event

    p1 = TimeRange(CD(4), CD(8))
    ES.overlay_availability(ev, p1)

    return (ev, ES, CD)


def testing_scenario2(a, b):
    (ev, ES, CD) = testing_scenario1(a, b)

    # overlap start/end of events

    p2 = TimeRange(CD(7), CD(9))
    ES.overlay_availability(ev, p2)

    # contain one event within another

    p3 = TimeRange(CD(5), CD(6))
    ES.overlay_availability(ev, p3)

    return (ev, ES, CD)

@ptest
def overlay_availability_test():
    (ev, ES, CD) = testing_scenario1(3, 10)
    expect(ES._event_lists[ev].first.next.key, CD(4))
    expect(ES._event_lists[ev].first.next.accum, 1)
    expect(ES._event_lists[ev].first.next.next.key, CD(8))
    expect(ES._event_lists[ev].first.next.next.accum, 0)

    (ev, ES, CD) = testing_scenario2(3, 10)
    expect(ES._event_lists[ev].first.next.key, CD(4))
    expect(ES._event_lists[ev].first.next.accum, 1)
    expect(ES._event_lists[ev].first.next.next.key, CD(5))
    expect(ES._event_lists[ev].first.next.next.accum, 2)
    expect(ES._event_lists[ev].first.next.next.next.key, CD(6))
    expect(ES._event_lists[ev].first.next.next.next.accum, 1)
    expect(ES._event_lists[ev].first.next.next.next.next.key, CD(7))
    expect(ES._event_lists[ev].first.next.next.next.next.accum, 2)
    expect(ES._event_lists[ev].first.next.next.next.next.next.key, CD(8))
    expect(ES._event_lists[ev].first.next.next.next.next.next.accum, 1)
    expect(ES._event_lists[ev].first.next.next.next.next.next.next.key, CD(9))
    expect(ES._event_lists[ev].first.next.next.next.next.next.next.accum, 0)
    expect(ES._event_lists[ev].first.next.next.next.next.next.next.next.key, None)
    expect(ES._event_lists[ev].first.next.next.next.next.next.next.next, ES._event_lists[ev].last)


@ptest
def overlay_availability_test_2():

    (ev, ES, CD) = testing_scenario2(3, 10)
    for result in ES.calc_times(ev):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(3, 10)
    for result in ES.calc_times(ev, max_missing=1):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(6, 10)
    for result in ES.calc_times(ev, max_missing=1):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(2, 5)
    for result in ES.calc_times(ev, max_missing=1):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(2, 6)
    for result in ES.calc_times(ev, max_missing=1):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(2, 4)
    for result in ES.calc_times(ev, max_missing=1):
        print(str(result))

    print("    ")

    (ev, ES, CD) = testing_scenario2(5, 7)
    for result in ES.calc_times(ev, max_missing=0):
        print(str(result))

# ----

if __name__ == "__main__":
    import builtins as __builtin__
    _print = __builtin__.print
    _replacement_print = lambda i: _print("\t" + str(i))
    __builtin__.print = _replacement_print

    for f in __tests:
        _print(f"\n########################################\nStarting test: \"{f[1]}\"")

        try:
            f[0]()
        except Exception:
            __builtin__.print = _print
            traceback.print_exc()
            __builtin__.print = _replacement_print
