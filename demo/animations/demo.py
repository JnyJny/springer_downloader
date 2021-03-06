#!/usr/bin/env python

"""
Demo Echoing 

Argv is a list of strings, each of which have embedded semicolons
indicating the end of a command.

Echos the "commands" to stdout using random jitter to simulate
being typed by a person. 

Runs the command in a subprocess homed in /tmp to time the
echoing of the next command.

This a hack.
"""

import subprocess

from random import random, choice
from sys import argv
from time import sleep
from string import printable


def delayed_echo(v) -> None:
    """
    """
    print(v, sep="", end="", flush=True)
    sleep(random() / 3)


def do_typo():
    """
    """
    delayed_echo(choice(printable))
    delayed_echo("")


if __name__ == "__main__":

    cmds = []

    for arg in argv[1:]:
        for c in arg.strip().split(";"):
            c = c.strip()
            if not len(c):
                continue
            cmds.append(c)

    if not cmds[-1].startswith("exit"):
        cmds.append("exit")

    for cmd in cmds:

        try:
            sleep(float(cmd))
            continue
        except ValueError:
            sleep(0.2)

        # echo the command to stdout with a random cadence

        for c in cmd:
            if random() <= 0.05:
                do_typo()
            delayed_echo(c)
        print(flush=True)
