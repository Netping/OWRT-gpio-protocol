#!/usr/bin/python3
import os
import sys

def help():
    print(f"Usage: {sys.argv[0]} <version>")

if __name__ == "__main__":
    expected_version = "0.1"

    if len(sys.argv) != 2:
        help()
        sys.exit(-1)

    if sys.argv[1] != expected_version:
        print(f"Wrong version! Expected \" {expected_version} \"")
        sys.exit(-2)

    print("OWRT-gpio-protocol")
    print(f"Version {expected_version}")

    os.system("pytest --capture=no -v test.py")
    sys.exit(0)