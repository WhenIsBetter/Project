import os
import glob
import traceback
import subprocess

TEST_DIR = "./testing/"

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
        process.wait()
    except Exception:
        print(f"\033 Test threw exception. \033[0m")
        traceback.print_exc()
    print("", flush=True)


sys.exit(1)