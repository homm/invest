#!/usr/bin/env python

import sys
import argparse
from datetime import datetime, timedelta

from _conf import CONF_PROLOGUE, default_tickers
from _client import InvestClient
from _crypto import prompt_cipher, decode_token, enc_token
from _crypto import command_set_token, command_change_password


def command_operations_log(date_from, date_to, group):
    cipher = prompt_cipher()
    client = InvestClient(decode_token(cipher, enc_token))
    client.list_operations(date_from, date_to, group=group)


def command_current_rate(tickers):
    if not tickers:
        if not default_tickers:
            sys.exit(f'usage: {sys.argv[0]} rates [tickers [tickers ...]]')
        tickers = default_tickers 
    else:
        print(f"""
{CONF_PROLOGUE}
default_tickers = "{' '.join(tickers)}"
""",
            file=sys.stderr
        )
    print('>>> show tickers', tickers)


def get_parser():
    def parse_date(date):
        return datetime.strptime(date, "%Y-%m-%d").date()

    next_day = (datetime.now() + timedelta(days=1)).date()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparser = subparsers.add_parser('log')
    subparser.set_defaults(command=command_operations_log)
    subparser.add_argument('--from', type=parse_date, dest='date_from',
                           required=True)
    subparser.add_argument('--to', type=parse_date, dest='date_to',
                           default=next_day)
    subparser.add_argument('--group', action='store_true')

    subparser = subparsers.add_parser('rates')
    subparser.set_defaults(command=command_current_rate)
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
