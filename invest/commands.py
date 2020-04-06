import sys
from getpass import getpass

from .conf import CONF_PROLOGUE, default_tickers, enc_token
from .client import InvestClient, group_operations
from .crypto import (decode_token, output_conf, prompt_cipher,
                     prompt_new_password)


def set_token():
    password = prompt_new_password()

    print(
        "Now please paste the token once. \nDo not store it anywhere else.",
        file=sys.stderr
    )
    token = getpass('Paste token: ')
    print("", file=sys.stderr)

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
    if callable(date_to):
        date_to = date_to()
    client = _get_client()
    
    operations = client.list_operations(date_from, date_to)
    if group:
        operations = group_operations(operations)

    print("\t".join(["Ticker", "Name", "Date", "Quantity", "Sum",
                     "Currency", "Sum (USD)"]))
    for (ticker, name, date, quantity, summ, currency, summ_base) in operations:
        if not quantity:
            quantity = ''
        print("\t".join([
            ticker, name, date, str(quantity),
            f"{summ:0.2f}", currency, f"{summ_base:0.2f}"
        ]))


def current_rates(tickers):
    if not tickers:
        if not default_tickers:
            sys.exit(f'usage: {sys.argv[0]} rates [tickers [tickers ...]]')
        tickers = default_tickers 
    else:
        print(
            f"""
{CONF_PROLOGUE}
default_tickers = "{' '.join(tickers)}"
""",
            file=sys.stderr
        )

    client = _get_client()
    client.tickers_rates(tickers)


def portfolio():
    client = _get_client()
    client.portfolio()
