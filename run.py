#!/usr/bin/env python

import sys
import argparse

from invest import commands
from invest.parsers import FromToDateParser
from invest.conf import enc_token


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparser = subparsers.add_parser('log')
    subparser.set_defaults(command=commands.operations_log)
    date_parser = FromToDateParser(default_to=FromToDateParser.next_day())
    subparser.add_argument(
        '--from', type=date_parser.parse_date, dest='date_from', required=True,
        help='The start date for the log. Required. Should be in 1999-12-31 '
             'format. Day or month could be omitted. In this case `--from` '
             'also sets the default value for `--to` argument. For example, '
             '`--from 2020-02-01 --to 2020-03-01` could be replaced '
             'with just `--from 2020-02`.',
    )
    subparser.add_argument(
        '--to', type=date_parser.parse_date, dest='date_to',
        default=date_parser.get_default_to,
        help='The finish date for the log, not including. Should be in '
             '1999-12-31 format. Default is one day in the future '
             '(show records until now). Day or month could be omitted. '
             '`--from 2020-04 --to 2020-06` means "show all records for '
             'April and May".',
    )
    subparser.add_argument(
        '--group', action='store_true',
        help='Groups records with the same Ticker, Name, and Currency. '
             'This can significantly reduce number of the records. '
             'Quantity and Sum columns will be summed up.',
    )

    subparser = subparsers.add_parser('rates')
    subparser.set_defaults(command=commands.current_rates)
    subparser.add_argument('tickers', nargs='*')

    subparser = subparsers.add_parser('portfolio')
    subparser.set_defaults(command=commands.portfolio)

    subparser = subparsers.add_parser('set_token')
    subparser.set_defaults(command=commands.set_token)

    subparser = subparsers.add_parser('change_password')
    subparser.set_defaults(command=commands.change_password)

    return parser


if __name__ == '__main__':
    if enc_token is None:
        print("Seems like this is the first run. "
              "Please fill the credentials to continue. "
              "At first, you need to choose a password.\n",
              file=sys.stderr)
        commands.set_token()
    else:
        args = vars(get_parser().parse_args())
        args.pop('command')(**args)
