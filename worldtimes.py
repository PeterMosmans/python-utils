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
    import pytz
    import tzlocal
except ImportError as exception:
    print(exception, file=sys.stderr)
    sys.exit(-1)

VERSION = '0.4'
DEFAULT_TIMEZONES = ['Australia/Sydney', 'Australia/Brisbane',
                     'Asia/Kuala_Lumpur', 'Asia/Singapore',
                     'Europe/Amsterdam', 'UTC', 'America/Chicago',
                     'US/Mountain']


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
    parser.add_argument('--from', action='store', type=str,
                        help='Timezone of the current or specified time')
    parser.add_argument('--to', action='store',
                        help='Timezone to convert to')
    parser.add_argument('--list', action='store_true',
                        help='List all timezones')
    parser.add_argument('--country', action='store',
                        help='List all timezones from country [in ISO 3166]')
    return vars(parser.parse_args())


def main():
    """Main program loop."""
    banner = 'worldtimes version {0}'.format(VERSION)
    time_format = '%z %Y-%m-%d %H:%M %Z'
    options = parse_arguments(banner)
    timezones = DEFAULT_TIMEZONES
    try:
        if not options['from']:
            timezone_from = tzlocal.get_localzone()
        else:
            timezone_from = pytz.timezone(options['from'])
    except pytz.exceptions.UnknownTimeZoneError as exception:
        print('Unknown timezone: {0}'.format(options['from']))
        sys.exit(-1)
    time_from = datetime.now(pytz.timezone('UTC'))
    try:
        if options['country']:
            print(' '.join(pytz.country_timezones[options['country']]))
            sys.exit(0)
        if options['time']:
            print('Using timezone {0} for specified time {1}'.format(timezone_from,
                                                                     options['time']))
            time_from = timezone_from.localize(datetime.strptime(time_from.
                                                                 strftime('%Y-%m-%d ') +
                                                                 options['time'],
                                                                 '%Y-%m-%d %H:%M'))
        if options['to'] and options['to'] in pytz.all_timezones_set:
            if options['to'] not in timezones:
                timezones = [options['to']] + timezones
        if options['from'] in pytz.all_timezones_set:
            if options['from'] not in timezones:
                timezones = [options['from']] + timezones
    except pytz.exceptions.UnknownTimeZoneError as exception:
        print('Unknown timezone: {0}'.format(exception), file=sys.stderr)
        sys.exit(-1)
    except KeyError as exception:
        print('Could not find country code: {0}'.format(exception), file=sys.stderr)
        sys.exit(-1)
    except ValueError as exception:
        print('Could not convert time: {0}'.format(exception), file=sys.stderr)
        sys.exit(-1)
    if options['list']:
        print(' '.join(pytz.all_timezones_set))
        sys.exit(0)
    timezone_times = [(item, time_from.astimezone(pytz.timezone(item)).
                       strftime(time_format)) for item in timezones]
    sorted(timezone_times, key=lambda x: int(x[1].split()[0]))
    for timezone, timestring in timezone_times:
        print('{0:20} {1}'.format(timezone, timestring))


if __name__ == "__main__":
    main()
