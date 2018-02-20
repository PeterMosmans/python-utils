#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""worldtimes - Display times and convert times between timezones

Copyright (C) 2017-2018 Peter Mosmans [Go Forward]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from datetime import datetime
import sys
import textwrap

try:
    import colorama
    import pytz
    import termcolor
    import tzlocal
except ImportError as exception:
    print('Please install all required libraries (see requirements.txt): {0}'.format(exception),
          file=sys.stderr)
    sys.exit(-1)

VERSION = '0.8'
DEFAULT_TIMEZONES = ['Australia/Sydney', 'Australia/Brisbane',
                     'Asia/Kuala_Lumpur', 'Asia/Singapore',
                     'Europe/Amsterdam', 'UTC', 'America/Chicago',
                     'US/Mountain']


def display_times(timezone_times, from_timezone, to_timezone):
    """Display times in each timezone."""
    colorama.init()
    for timezone, timestring in timezone_times:
        if timezone.lower() == unicode(from_timezone).lower():
            termcolor.cprint('{0:20} {1}'.format(timezone, timestring),
                             'green', attrs=['bold'])
        elif timezone.lower() == unicode(to_timezone).lower():
            termcolor.cprint('{0:20} {1}'.format(timezone, timestring),
                             attrs=['bold'])
        else:
            print('{0:20} {1}'.format(timezone, timestring))


def list_countries(country):
    """List available country codes and exit."""
    try:
        print(' '.join(pytz.country_timezones[country]))
    except KeyError as exception:
        print('Could not find country: {0}'.format(exception), file=sys.stderr)
    sys.exit(0)


def parse_arguments(banner):
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner + '''\
 - Display times and convert times between timezones

Copyright (C) 2017-2018 Peter Mosmans [Go Forward]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument('time', nargs='?', type=str,
                        help='Time to convert in HH:MM')
    parser.add_argument('--date', action='store', type=str,
                        help='Specific date to convert in YYYY-MM-DD')
    parser.add_argument('--from', action='store', type=str,
                        help='Timezone of the current or specified time')
    parser.add_argument('--to', action='store',
                        help='Timezone to convert to')
    parser.add_argument('--list', action='store_true',
                        help='List all timezones')
    parser.add_argument('--country', action='store',
                        help='List all timezones from country [in ISO 3166]')
    return vars(parser.parse_args())


def set_datetime(from_time, from_date, from_timezone):
    """Set the datetime according to time, date and timezone."""
    try:
        time_from = datetime.now(from_timezone)
        if not from_time:
            from_time = time_from.strftime('%H:%M')
        if not from_date:
            from_date = time_from.strftime('%Y-%m-%d')
        time_from = from_timezone.localize(datetime.strptime(from_date + ' ' +
                                                             from_time,
                                                             '%Y-%m-%d %H:%M'))
    except ValueError as exception:
        print('Could not convert time: {0}'.format(exception), file=sys.stderr)
        sys.exit(-1)
    return time_from


def sort_times(timezones, from_datetime, additional_zones):
    """Add additional zones, and create a list of sorted times according to timezone."""
    for zone in additional_zones:
        if unicode(zone) not in timezones:
            timezones.append(unicode(zone))
    sorted_times = [(item, from_datetime.astimezone(pytz.timezone(item)).
                     strftime('%z %Y-%m-%d %H:%M %Z')) for item in timezones]
    sorted(sorted_times, key=lambda x: int(x[1].split()[0]))
    return sorted_times


def validate_timezones(from_timezone, to_timezone):
    """Validate timezones."""
    try:
        if not from_timezone:
            from_timezone = tzlocal.get_localzone()
        else:
            from_timezone = pytz.timezone(from_timezone.title())
        if not to_timezone:
            to_timezone = tzlocal.get_localzone()
        else:
            to_timezone = pytz.timezone(to_timezone.title())
    except pytz.exceptions.UnknownTimeZoneError as exception:
        print('Unknown timezone: {0}'.format(exception))
        sys.exit(-1)
    return from_timezone, to_timezone


def main():
    """Main program loop."""
    banner = 'worldtimes version {0}'.format(VERSION)
    options = parse_arguments(banner)
    if options['list']:
        print(' '.join(pytz.all_timezones_set))
        sys.exit(0)
    if options['country']:
        list_countries(options['country'])
    timezones = DEFAULT_TIMEZONES
    from_timezone, to_timezone = validate_timezones(options['from'], options['to'])
    from_datetime = set_datetime(options['time'], options['date'], from_timezone)
    sorted_times = sort_times(timezones, from_datetime, [from_timezone, to_timezone])
    display_times(sorted_times, from_timezone, to_timezone)


if __name__ == "__main__":
    main()
