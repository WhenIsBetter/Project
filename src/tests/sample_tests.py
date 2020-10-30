from src.main.DiscordBot import DiscordBot

__tests = []

def ptest(test, message = None):
    if message is None:
        message  = test.__name__
    global __tests
    __tests.append([test, message])
    return test

# ----

@ptest
def testBot():
    TOKEN = open("../../deploy/token.txt", "r").read()
    bot = DiscordBot(TOKEN)
    print(f"Logged in and ready to go!")
    bot.run()



# ----

if __name__ == "__main__":
    import builtins as __builtin__
    _print = __builtin__.print
    __builtin__.print = lambda i: _print("\t" + i)

    for f in __tests:
        _print(f"Starting test: \"{f[1]}\"")
        f[0]()
