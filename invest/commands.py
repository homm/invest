import sys
from getpass import getpass

from .conf import CONF_PROLOGUE, default_tickers, enc_token
from .client import InvestClient
from .crypto import (decode_token, output_conf, prompt_cipher,
                     prompt_new_password)


def set_token():
    password = prompt_new_password()

    print("""
Now please paste the token once.
Do not store it anywhere else.
""", file=sys.stderr)
    token = getpass('Paste token: ')

    output_conf(password, token)


def change_password():
    old_cipher = prompt_cipher()
    token = decode_token(old_cipher, enc_token)

    password = prompt_new_password()

    output_conf(password, token)


def _get_client():
    cipher = prompt_cipher()
    return InvestClient(decode_token(cipher, enc_token))


def operations_log(date_from, date_to, group):
    client = _get_client()
    client.list_operations(date_from, date_to, group=group)


def current_rates(tickers):
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

    client = _get_client()
    client.tickers_rates(tickers)
