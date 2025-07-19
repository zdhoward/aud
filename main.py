#!/usr/bin/python3

from aud import Dir


def main():
    """Simple entry point used for manual testing."""
    a = Dir("mock")
    a.config_set_extensions(["wav"])
    return a.get_all()


if __name__ == "__main__":
    print(main())
