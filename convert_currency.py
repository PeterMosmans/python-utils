#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""convert_currency - Convert between currencies using official exchange rates

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
    from forex_python.converter import CurrencyRates, RatesNotAvailableError
except ImportError as exception:
    print('This script needs external pip libraries: {0}'.format(exception),
          file=sys.stderr)
    print('Install the missing libraries using pip -r requirements.txt',
          file=sys.stderr)
    sys.exit(-1)

VERSION = '0.5'


def calculate_fees(amount, fee, decimals):
    """Calculate amount minus and plus fees, rounded to specified number of decimals."""
    add_fee = round(amount * (fee/100), decimals)
    subtract_fee = round(amount / (fee/100), decimals)
    return add_fee, subtract_fee


def parse_arguments(banner):
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner + '''\
 - Convert between currencies using official exchange rates

Copyright (C) 2017-2018 Peter Mosmans [Go Forward]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument('amount', nargs='?', type=float,
                        help='Amount to convert')
    parser.add_argument('--amount', action='store', type=float,
                        help='Amount to convert from')
    parser.add_argument('--date', action='store', default=datetime.strftime(datetime.today(),
                                                                            '%Y-%m-%d'),
                        help='Specify date (default today, %(default)s)')
    parser.add_argument('--fee', action='store', type=float, default=2.5,
                        help=r'Exchange rate fee in %% (default %(default)s)')
    parser.add_argument('--from', action='store', default='EUR',
                        help='Currency symbol to convert from (default %(default)s)')
    parser.add_argument('--to', action='store', default='EUR',
                        help='Currency symbol to convert to (default %(default)s)')
    return vars(parser.parse_args())


def main():
    """Main program loop."""
    banner = 'convert_currency version {0}'.format(VERSION)
    options = parse_arguments(banner)
    options['fee'] = 100 + options['fee']
    try:
        options['date'] = datetime.strptime(options['date'], '%Y-%m-%d')
    except ValueError as exception:
        print('Dates must be in the form YYYY-mm-dd: {0}'.format(exception, file=sys.stderr))
        sys.exit(-1)
    rates = CurrencyRates()
    print('Converting from {0} to {1}'.format(options['from'], options['to']))
    try:
        rate = rates.get_rate(options['from'], options['to'], options['date'])
        add_fee, subtract_fee = calculate_fees(rate, options['fee'], 5)
        print('{0}    {1:>10} {2:>10} {3:>10}'.format(options['date'].
                                                      strftime('%Y-%m-%d'),
                                                      subtract_fee, rate,
                                                      add_fee))
        if options['amount']:
            total = round(rate * options['amount'], 2)
            add_fee, subtract_fee = calculate_fees(total, options['fee'], 2)
            print(' {0:>6} {1} = {2:>10} {3:>10} {4:>10} {5}'.format(options['amount'],
                                                                     options['from'],
                                                                     subtract_fee,
                                                                     total,
                                                                     add_fee,
                                                                     options['to']))
    except RatesNotAvailableError as exception:
        print('Could not convert rates: {0}'.format(exception), file=sys.stderr)





if __name__ == "__main__":
    main()
