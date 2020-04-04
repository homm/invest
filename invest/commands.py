import sys

from .conf import CONF_PROLOGUE, default_tickers, enc_token
from .client import InvestClient
from .crypto import prompt_cipher, decode_token


def operations_log(date_from, date_to, group):
    cipher = prompt_cipher()
    client = InvestClient(decode_token(cipher, enc_token))
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
    print('>>> show tickers', tickers)
