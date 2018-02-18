############
python-utils
############

A collection of various utilities (scripts), written in Python.
Don't forget to install the necessary dependencies that are specified in
:code:`requirements.txt`:

:code:`pip install -r requirements.txt`


*******************
convert_currency.py
*******************

::

   usage: convert_currency.py [-h] [--amount AMOUNT] [--date DATE] [--fee FEE]
                              [--from FROM] [--to TO]
                              [amount]

   convert_currency version 0.5 - Convert between currencies using official exchange rates

   Copyright (C) 2017-2018 Peter Mosmans [Go Forward]

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   positional arguments:
     amount           Amount to convert

   optional arguments:
     -h, --help       show this help message and exit
     --amount AMOUNT  Amount to convert from
     --date DATE      Specify date (default today, 2018-02-18)
     --fee FEE        Exchange rate fee in % (default 2.5)
     --from FROM      Currency symbol to convert from (default EUR)
     --to TO          Currency symbol to convert to (default EUR)

Usage examples
==============

Convert USD 500 to EUR on 2013-03-07

::
  
   % ./convert_currency.py --from USD 500 --date 2013-03-07
   
   Converting from USD to EUR
   2013-03-07       0.74989    0.76864    0.78786
     500.0 USD =     374.95     384.32     393.93 EUR

*************
worldtimes.py
*************

::

   usage: worldtimes.py [-h] [--date DATE] [--from FROM] [--to TO] [--list]
                        [--country COUNTRY]
                        [time]

   worldtimes version 0.7 - Display times and convert times between timezones

   Copyright (C) 2017-2018 Peter Mosmans [Go Forward]

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   positional arguments:
     time               Time to convert in HH:MM

   optional arguments:
     -h, --help         show this help message and exit
     --date DATE        Specific date to convert in YYYY-MM-DD
     --from FROM        Timezone of the current or specified time
     --to TO            Timezone to convert to
     --list             List all timezones
     --country COUNTRY  List all timezones from country [in ISO 3166]

The script contains a number of default timezones.

Usage examples
==============

Convert a time from UTC 2013-03-07 13:37 to various other timezones

::

   % ./worldtimes.py --from UTC --date 2013-3-7 13:37

   Australia/Sydney     +1100 2013-03-08 00:37 AEDT
   Australia/Brisbane   +1000 2013-03-07 23:37 AEST
   Asia/Kuala_Lumpur    +0800 2013-03-07 21:37 +08
   Asia/Singapore       +0800 2013-03-07 21:37 +08
   Europe/Amsterdam     +0100 2013-03-07 14:37 CET
   UTC                  +0000 2013-03-07 13:37 UTC
   America/Chicago      -0600 2013-03-07 07:37 CST
   US/Mountain          -0700 2013-03-07 06:37 MST

See what time it currently is in New York time (America/New_York)

::

   % ./worldtimes.py --to America/New_York

   Australia/Sydney     +1100 2018-02-16 12:09 AEDT
   Australia/Brisbane   +1000 2018-02-16 11:09 AEST
   Asia/Kuala_Lumpur    +0800 2018-02-16 09:09 +08
   Asia/Singapore       +0800 2018-02-16 09:09 +08
   Europe/Amsterdam     +0100 2018-02-16 02:09 CET
   UTC                  +0000 2018-02-16 01:09 UTC
   America/Chicago      -0600 2018-02-15 19:09 CST
   US/Mountain          -0700 2018-02-15 18:09 MST
   America/New_York     -0500 2018-02-15 20:09 EST

