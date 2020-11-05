import os, glob
import traceback
import asyncio

TEST_DIR = "./testing/"
async def main():
    for filename in glob.glob(os.path.join(TEST_DIR, '*.test.py')):
        with open(filename, 'r') as f:
            try:
                greeting = f"\033[1m\033[92mRunning Test:\033[0m {filename}"
                length = len(greeting) - 9
                banner = "###" + (''.join( ['-'] * (length - 6))) + "###"
                print("\n" + banner)
                print(greeting)
                print(banner + "\n")

                print("", flush=True)
                await exec(f.read())
                print("", flush=True)

            except Exception:
                print(f"\033 Test threw exception. \033[0m")
                traceback.print_exc()

asyncio.get_event_loop().run_until_complete(main())