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

from random import random
from sys import argv
from time import sleep


if __name__ == "__main__":

    cmds = []

    for arg in argv[1:]:
        for c in arg.strip().split(";"):
            if not len(c):
                continue
            cmds.append(c)

    sleep(1)
    for cmd in cmds:
        # echo the command to stdout with
        # a random cadence
        for c in cmd:
            print(c, sep="", end="", flush=True)
            sleep(random() / 5)
        print(flush=True)

        # execute the same command with
        # cwd = /tmp to avoid echoing the
        # next command before the current
        # one is finished in the screen recorder.
        #
        # Should do some timing of the subprocess
        # and do a logrithmic backoff (short
        # runtimes have a short idle, long
        # runtimes have a much longer idle to
        # take into account jitter in longer
        # running commands (eg. download)

        results = subprocess.run(
            cmd.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd="/tmp",
        )

        sleep(60)
