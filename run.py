import argparse
from datetime import datetime, timedelta

from _client import InvestClient
from _crypto import prompt_cipher, decode_token, enc_token
from _crypto import command_set_token, command_change_password


def command_list_operations(date_from, date_to, group):
    cipher = prompt_cipher()
    client = InvestClient(decode_token(cipher, enc_token))
    client.list_operations(date_from, date_to, group=group)


def get_parser():
    def parse_date(date):
        return datetime.strptime(date, "%Y-%m-%d").date()

    next_day = (datetime.now() + timedelta(days=1)).date()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparser = subparsers.add_parser('list')
    subparser.set_defaults(command=command_list_operations)
    subparser.add_argument('--from', type=parse_date, dest='date_from',
                           required=True)
    subparser.add_argument('--to', type=parse_date, dest='date_to',
                           default=next_day)
    subparser.add_argument('--group', action='store_true')

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
