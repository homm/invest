import sys
from getpass import getpass

from .conf import CONF_PROLOGUE, enc_token
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


def operations_log(date_from, date_to, group, account):
    if callable(date_to):
        date_to = date_to()
    client = _get_client()

    account = client.search_account_id(account)
    operations = client.list_operations(date_from, date_to, account=account)
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


def accounts():
    client = _get_client()
    for account in client.get('user/accounts')['accounts']:
        print(f"{account['brokerAccountType']}: {account['brokerAccountId']}")


def portfolio(account):
    client = _get_client()

    account = client.search_account_id(account)
    client.portfolio(account)
