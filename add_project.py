#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" add_project - Adds Camtasia project files to git

Copyright (C) 2017-2019 Peter Mosmans [Go Forward]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import glob
import json
import logging
import re
import os
import subprocess
import sys
import textwrap


NAME = "add_project"
__version__ = "0.2"


class LogFormatter(logging.Formatter):
    """Class to format log messages based on their type."""

    FORMATS = {
        logging.DEBUG: "[d] %(message)s",
        logging.INFO: "[*] %(message)s",
        logging.ERROR: "[-] %(message)s",
        logging.CRITICAL: "[-] FATAL: %(message)s",
        "DEFAULT": "%(message)s",
    }

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        return logging.Formatter.format(self, record)


class LogFilter(object):  # pylint: disable=too-few-public-methods
    """Class to remove certain log levels."""

    def __init__(self, filterlist):
        self.__filterlist = filterlist

    def filter(self, logRecord):  # pylint: disable=invalid-name
        """Remove logRecord if it is part of filterlist."""
        return logRecord.levelno not in self.__filterlist


def execute_command(cmd):
    """Executes command."""
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        result = process.returncode
    except OSError as exception:
        result = -1
        logging.error("Could not execute %s: %s", cmd, exception.strerror)
    logging.debug(stdout)
    return result == 0


def git_add(filename):
    execute_command(["git", "add", filename])


def make_relative(filename):
    """Replace absolute paths with relative paths."""
    current = os.getcwd().replace("/", r"\\") + r"\\"
    rewrite_file(filename, current, "")


def rewrite_file(filename, old, new):
    """Change string in file from old to new."""
    with open(filename) as f:
        buffer = f.read()

    if buffer.lower().find(old.lower()):
        replacer = re.compile(re.escape(old), re.IGNORECASE)
        logging.info("Replacing %s with %s in %s", old, new, filename)
        with open(filename, "w") as f:
            f.write(replacer.sub(new, buffer))


def parse_arguments(banner):
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            banner
            + """\
        - Adds Camtasia project files to git

        Copyright (C) 2017-2019 Peter Mosmans [Go Forward]

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version."""
        ),
    )
    parser.add_argument(
        "input", nargs="?", type=str, help="""[INPUTFILE] can be TODO"""
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--debug", action="store_true", help="Show debug information")
    parser.add_argument("--fix", action="store", help="Try to fix paths")
    parser.add_argument(
        "--relative",
        action="store_true",
        help="Rewrite absolute paths to relative paths",
    )
    parser.add_argument("--current", type=str, help="Current path in project file")
    parser.add_argument(
        "--new", type=str, help="New path to replace current path with in project file"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Be more verbose")
    args = parser.parse_args()
    if args.version:
        print(banner)
        sys.exit(0)
    return args


def setup_logging(args):
    """Set up loghandlers according to options."""
    logger = logging.getLogger()
    logger.setLevel(0)
    console = logging.StreamHandler(stream=sys.stdout)
    console.addFilter(LogFilter([logging.ERROR]))
    console.setFormatter(LogFormatter())
    if args.debug:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    logger.addHandler(console)
    # Set up a stderr loghandler which only shows error message
    errors = logging.StreamHandler(stream=sys.stderr)
    errors.setLevel(logging.ERROR)
    logger.addHandler(errors)


def parse_project(project, args):
    """Parse a project file."""
    if not os.path.isfile(project):
        return
    if args.relative:
        make_relative(project)
    if args.fix:
        rewrite_file(project, args.fix, "")
    git_add(project)
    parsed = json.load(open(project))
    if "sourceBin" in parsed:
        sources = parsed["sourceBin"]
        logging.info("%s uses the following resources:", project)
        for src in sources:
            source = src["src"]
            if "ProgramData" not in source:
                logging.info("Adding %s", source)
                # if args["current"] and args["new"] and args["current"] in source:
                #     source = source.replace(args["current"], args["new"])
                #     print(f"replacing to {source}"
                if not os.path.isfile(source):
                    log.error("WARNING: %s cannot be found", source)
                    sys.exit(-1)
                git_add(source)


def main():
    """Main program loop."""
    banner = f"{NAME} version {__version__}"
    args = parse_arguments(banner)
    setup_logging(args)
    if args.input:
        if args.relative:
            make_relative(args.input)
            sys.exit(0)
        projects = [parse_project(args.input)]
    else:
        projects = glob.glob(os.path.join("./m?/*.tscproj"))
    for project in projects:
        parse_project(project, args)


if __name__ == "__main__":
    main()
