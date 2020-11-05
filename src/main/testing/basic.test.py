import multiprocessing
import traceback
import time

from spm_bot.DiscordBot import DiscordBot

testBot_sleepTime = 2

def testBot():
    TOKEN = open("../../deploy/token.txt", "r").read()
    bot = DiscordBot()
    print(f"Logged in and ready to go!")
    bot.run(TOKEN)

if __name__ == "__main__":
    try:
        p = multiprocessing.Process(target=testBot, name="Basic Test", args=())
        p.start()
        time.sleep(testBot_sleepTime)
        p.terminate()
        p.join()
    except Exception:
        traceback.print_exc()