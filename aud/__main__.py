import sys
import pytest

if "--test" in sys.argv:
    sys.exit(pytest.main(["-x", "-v"]))
elif len(sys.argv) > 1:
    print("--test is the only valid option")
