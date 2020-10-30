import multiprocessing
import time
import traceback

import datetime
from src.main.TimeRange import TimeRange

from src.main.DiscordBot import DiscordBot

__tests = []

def ptest(test, message = None):
    if message is None:
        message  = test.__name__
    global __tests
    __tests.append([test, message])
    return test

def busy_ptest_f(delay = 2, message = None):
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

# ----

if __name__ == "__main__":
    import builtins as __builtin__
    _print = __builtin__.print
    _replacement_print = lambda i: _print("\t" + i)
    __builtin__.print = _replacement_print

    for f in __tests:
        _print(f"\n########################################\nStarting test: \"{f[1]}\"")

        try:
            f[0]()
        except Exception:
            __builtin__.print = _print
            traceback.print_exc()
            __builtin__.print = _replacement_print
