#!/usr/bin/python3

from aud import Dir


def main():
    a = Dir("mock")
    a.config_set_extensions(["wav"])
    return a.get_all()


if __name__ == "__main__":
    print(main())
