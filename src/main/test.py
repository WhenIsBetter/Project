import os
import sys
import glob
import traceback
import subprocess

TEST_DIR = "./testing/"

return_val = 0

for filename in glob.glob(os.path.join(TEST_DIR, '*.test.py')):
    greeting = f"\033[1m\033[92mRunning Test:\033[0m {filename}"
    length = len(greeting) - 9
    banner = "###" + (''.join( ['-'] * (length - 6))) + "###"
    print("\n" + banner)
    print(greeting)
    print(banner + "\n")

    print("", flush=True)
    try:
        os.system(f"export PYTHONPATH=$PWD:$PYTHONPATH")
        process = subprocess.Popen(["python3", filename])
        return_val = 1 if 0 != process.wait() else return_val
    except Exception:
        print(f"\033 Test threw exception. \033[0m")
        traceback.print_exc()
        return_val = 1
    print("", flush=True)

sys.exit( return_val )