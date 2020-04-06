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
    subparser.add_argument('--from', type=date_parser.parse_date,
                           dest='date_from', required=True)
    subparser.add_argument('--to', type=date_parser.parse_date,
                           dest='date_to', default=date_parser.get_default_to)
    subparser.add_argument('--group', action='store_true')

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
