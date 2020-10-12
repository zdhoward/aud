import sys
import os

if "--test" in sys.argv:
    os.system("pytest -xv")
elif len(sys.argv) > 1:
    print("--test is the only valid option")
