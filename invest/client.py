import sys
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests


class InvestClient(requests.Session):
    api_base = "https://api-invest.tinkoff.ru/openapi/"
    known_tickers = {
        "USD000UTSTOM": "USD",
    }
    known_figis = {
        "USD": "BBG0013HGFT4",
    }

    def __init__(self, token, default_timeout=5):
        super().__init__()
        self.default_timeout = default_timeout
        self.headers.update({
            "accept": "application/json",
            "Authorization": "Bearer " + token,
        })
        self._figi_cache = {}

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.api_base or '', url)
        kwargs.setdefault('timeout', self.default_timeout)
        return super().request(method, url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        resp = super().get(url, *args, **kwargs)
        if resp.status_code != 200:
            print(resp.status_code, resp.text, file=sys.stderr)
            raise ValueError(f"Can't get {url}")
        return resp.json()['payload']

    def search_account_id(self, needle):
        if not needle:
            return
        if needle.isdigit():
            return needle
        needle = needle.lower()
        if needle == 'iis':
            needle = 'tinkoff' + needle
        for account in self.get('user/accounts')['accounts']:
            if account['brokerAccountType'].lower() == needle:
                return account['brokerAccountId']
        raise ValueError(f'Account {needle} is not found.')

    def operations(self, date_from, date_to=None, figi=None, account=None):
        resp = self.get(
            "operations",
            params={
                "figi": figi,
                "from": date_from.strftime('%Y-%m-%d') + "T09:00:00+03:00",
                "to": date_to.strftime('%Y-%m-%d') + "T09:00:00+03:00",
                "brokerAccountId": account,
            },
        )
        return resp['operations']

    def search_by_figi(self, figi):
        if figi not in self._figi_cache:
            resp = self.get("market/search/by-figi", params={"figi": figi})
            if resp['ticker'] in self.known_tickers:
                resp['ticker'] = self.known_tickers[resp['ticker']]
            self._figi_cache[figi] = resp
        return self._figi_cache[figi]

    def search_last_op(self, date_to, days_back=60, op_type='Sell',
                       figi=None, account=None):
        date_from = date_to - timedelta(days=days_back)
        if not isinstance(op_type, (list, tuple)):
            op_type = (op_type,)
        operations = self.operations(date_from, date_to,
                                     figi=figi, account=account)
        for op in operations:
            if op["operationType"] in op_type:
                return op

    def list_operations(self, date_from, date_to, group=False, account=None):
        operations = self.operations(date_from, date_to, account=account)

        last_base_sell = None

        for op in reversed(operations):
            optype = op["operationType"]

            if op['status'] == "Decline":
                continue

            if optype in ("PayIn", "PayOut"):
                continue

            ticker, name, date, quantity, summ, currency = (
                '', optype, op['date'].split('T')[0],
                0, op['payment'], op['currency'])
            if 'figi' in op:
                figi = self.search_by_figi(op['figi'])
                ticker = figi['ticker']

            if optype in ("Buy", "BuyCard", "Sell"):
                if (ticker, optype) == ("USD", "Sell"):
                    last_base_sell = op
                name = figi['name']
                quantity = sum(trade['quantity'] for trade in op['trades'])
                quantity *= (-1 if optype == 'Sell' else 1)
            
            elif optype in ("BrokerCommission",):
                pass

            elif optype in ("Dividend", "TaxDividend", "Coupon"):
                name = figi['name'] + f" ({optype})"

            elif optype in ("Tax", "TaxBack"):
                ticker = "$TAX"

            elif optype in ("ServiceCommission",):
                ticker = "$COM"

            else:  # unknown
                print("Unknown operation type:", file=sys.stderr)
                print(json.dumps(op, indent=2), file=sys.stderr)
                continue

            summ_base = summ
            if currency == 'RUB':
                if last_base_sell is None:
                    last_base_sell = self.search_last_op(
                        date_from, figi=self.known_figis["USD"],
                        account=account)
                summ_base = round(summ / last_base_sell['price'], 2)

            yield (ticker, name, date, quantity, summ, currency, summ_base)

    def portfolio(self, account=None):
        resp = self.get('portfolio', params={'brokerAccountId': account})
        
        print("\t".join(["Ticker", "Name", "Quantity", "Price", "Currency"]))
        for pos in resp['positions']:
            ticker = self.known_tickers.get(pos['ticker'], pos['ticker'])
            price = pos['averagePositionPrice']['value']
            price += pos['expectedYield']['value'] / pos['balance']
            print("\t".join([
                ticker, pos['name'], str(int(pos['balance'])),
                f"{price:0.2f}", pos['expectedYield']['currency']
            ]))


def group_operations(operations):
    groups = {}
    for (ticker, name, date, quantity, summ, currency, summ_base) in operations:
        params = groups.setdefault((ticker, name, currency),
                                   [date, 0, 0, 0])
        params[1] += quantity
        params[2] += summ
        params[3] += summ_base

    for ((ticker, name, currency),
         (date, quantity, summ, summ_base)) in groups.items():
        yield (ticker, name, date, quantity, summ, currency, summ_base)
