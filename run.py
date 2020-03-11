import argparse

from _client import InvestClient
from _crypto import prompt_cipher, decode_token, enc_token
from _crypto import command_set_token, command_change_password


def command_list_operations(**kwargs):
    cipher = prompt_cipher()
    client = InvestClient(decode_token(cipher, enc_token))
    client.list_operations(**kwargs)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparser = subparsers.add_parser('list')
    subparser.set_defaults(command=command_list_operations)

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
