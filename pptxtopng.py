#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation

"""pptxtopng - Export PowerPoint slides as PNG files

Copyright (C) 2018-2019 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys
import textwrap
from shutil import copyfile


__title__ = "pptxtopng"
__version__ = "0.5.0"


try:
    import comtypes.client
except ImportError as exception:
    print(f"Please install all required libraries: {exception}",
          file=sys.stderr)
    sys.exit(-1)


class LogFormatter(logging.Formatter):
    """Class to format log messages based on their type."""
    # pylint: disable=protected-access
    FORMATS = {logging.DEBUG: logging._STYLES["{"][0]("[d] {message}"),
               logging.INFO: logging._STYLES["{"][0]("[*] {message}"),
               logging.ERROR: logging._STYLES["{"][0]("[-] {message}"),
               logging.CRITICAL: logging._STYLES["{"][0]("[-] FATAL: {message}"),
               "DEFAULT": logging._STYLES["{"][0]("{message}")}

    def format(self, record):
        self._style = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        return logging.Formatter.format(self, record)


class LogFilter():  # pylint: disable=too-few-public-methods
    """Class to remove certain log levels."""
    def __init__(self, filterlist):
        self.__filterlist = filterlist

    def filter(self, logRecord):  # pylint: disable=invalid-name
        """Remove logRecord if it is part of filterlist."""
        return logRecord.levelno not in self.__filterlist


def setup_logging(options):
    """Set up loghandlers according to options."""
    logger = logging.getLogger()
    logger.setLevel(0)
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(LogFormatter())
    # Set up a stderr loghandler which only shows error message
    errors = logging.StreamHandler(stream=sys.stderr)
    errors.setLevel(logging.ERROR)
    console.addFilter(LogFilter([logging.ERROR]))
    if options['debug']:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    logger.addHandler(console)
    logger.addHandler(errors)


def parse_arguments(banner):
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner + '''\
 - Export PowerPoint slides as PNG files

Copyright (C) 2018-2019 Peter Mosmans [Go Forward]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument("slides", nargs="?", type=str, default="slides.pptx",
                        help="PowerPoint slidedeck (default %(default)s)")
    parser.add_argument("--from", action="store", type=int,
                        help="Copy slide range from")
    parser.add_argument("--to", action="store", type=int,
                        help="Copy slide range to")
    parser.add_argument("--copy", action="store", type=str,
                        help="Copy slide range / section output folder")
    parser.add_argument("--section", action="store", type=int,
                        help="Copy specified section to output folder")
    parser.add_argument("--single", action="store", type=int,
                        help="Copy single slide")
    parser.add_argument("-o", "--output", action="store", type=str,
                        default=".", help="Output path (default %(default)s)")
    parser.add_argument('--debug', action='store_true',
                        help='Show debug information')
    return vars(parser.parse_args())


def get_presentation(powerpoint, path, name):
    """Retrieve Presentation object of specified slidedeck."""
    opened = False
    for presentation in powerpoint.Presentations:
        opened = ((presentation.Path == path) and presentation.Name == name)
        if opened:
            logging.debug("Presentation already open")
            break
    if not opened:
        if not os.path.isfile(path + '\\' + name):
            logging.error(r"Could not find %s\%s", path, name)
            sys.exit(-1)
        logging.debug("Opening presentation")
        presentation = powerpoint.Presentations.Open(path + '\\' + name)
    return presentation, opened


def windows_path(pathname):
    """Convert non-Windows pathname into Windows pathname."""
    return pathname.replace('/', '\\')


def get_section_range(presentation, section):
    """Return the start and end range of a specified section."""
    if section >= presentation.SectionProperties.Count:
        logging.error(f"This presentation only has {presentation.SectionProperties.Count} sections")
        sys.exit(-1)
    range_from = presentation.SectionProperties.FirstSlide(section)
    return range_from, range_from + presentation.SectionProperties.SlidesCount(section)


def get_powerpoint():
    """Open Powerpoint application."""
    try:
        powerpoint = comtypes.client.GetActiveObject("Powerpoint.Application")
    except WindowsError:
        logging.debug("Opening powerpoint")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    # powerpoint.Visible = True
    if not powerpoint:
        logging.error("Could not open PowerPoint")
        sys.exit(-1)
    return powerpoint


def check_file(name):
    """Checks whether filename and path exist."""
    if not os.path.isfile(name):
        logging.error(f"Could not find {name}")
        sys.exit(-1)


def check_path(path):
    """Check whether pathname exists."""
    if not os.path.isdir(path):
        logging.error("Could not find {path}")
        sys.exit(-1)


def copy_slides(source, dest, range_from, range_to, prefix=0):
    """Copy @rangefrom to @rangeto slides from@source to @destination"""
    logging.info(f"Copying slides {range_from} from {range_to} to {dest}")
    for index in range(range_from, range_to + 1):  # Include to
        file_source = os.path.join(source, f"Slide{index}.PNG")
        if os.path.isfile(file_source):
            file_dest = os.path.join(windows_path(os.path.join(os.getcwd(), dest)),
                                     f"Slide{prefix}-{index-range_from+1:02}.png")
            try:
                copyfile(file_source, file_dest)
            except (FileNotFoundError, PermissionError) as exception:
                logging.error(f"Could not copy {file_source} to {file_dest}:, {exception}")
        else:
            logging.error(f"Could not find slide {file_source}")


def close_presentation(powerpoint, slidename):
    """Close presentation and powerpoint, if no presentations are open."""
    for presentation in powerpoint.Presentations:
        if presentation.Name == slidename:
            logging.debug("Closing presentation")
            presentation.Close()
    if not powerpoint.Presentations.Count:
        logging.debug("Closing powerpoint")
        powerpoint.Quit()


def main():
    """Main program loop."""
    banner = f"{__title__} version {__version__}"
    options = parse_arguments(banner)
    setup_logging(options)
    slidedeck = windows_path(os.path.join(os.getcwd(), options['slides']))
    export_path = windows_path(os.path.join(os.getcwd(), options['output']))
    check_file(slidedeck)
    check_path(export_path)
    name, path = os.path.basename(slidedeck), os.path.dirname(slidedeck)
    powerpoint = get_powerpoint()
    presentation, opened = get_presentation(powerpoint, path, name)
    logging.info(f"Exporting presentation to {export_path}")
    presentation.Export(export_path, "png")
    if options["from"]:
        range_from = options["from"]
        if not options["to"]:
            range_to = range_from
    section = 0
    if options["section"]:
        section = options["section"]
        range_from, range_to = get_section_range(presentation, section)
    if not opened:
        close_presentation(powerpoint, name)
    if options["copy"]:
        copy_slides(export_path, options["copy"], range_from, range_to, section)


if __name__ == "__main__":
    main()
