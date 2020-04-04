#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta

from invest import commands
from invest.crypto import command_set_token, command_change_password, enc_token


def get_parser():
    def parse_date(date):
        return datetime.strptime(date, "%Y-%m-%d").date()

    next_day = (datetime.now() + timedelta(days=1)).date()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparser = subparsers.add_parser('log')
    subparser.set_defaults(command=commands.operations_log)
    subparser.add_argument('--from', type=parse_date, dest='date_from',
                           required=True)
    subparser.add_argument('--to', type=parse_date, dest='date_to',
                           default=next_day)
    subparser.add_argument('--group', action='store_true')

    subparser = subparsers.add_parser('rates')
    subparser.set_defaults(command=commands.current_rates)
    subparser.add_argument('tickers', nargs='*')

    subparser = subparsers.add_parser('set_token')
    subparser.set_defaults(command=command_set_token)

    subparser = subparsers.add_parser('change_password')
    subparser.set_defaults(command=command_change_password)

    return parser


if __name__ == '__main__':
    if enc_token is None:
        command_set_token()
    else:
        args = vars(get_parser().parse_args())
        args.pop('command')(**args)
