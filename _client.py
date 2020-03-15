import json
from datetime import timedelta
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

    def operations(self, date_from, date_to=None, figi=None):
        res = self.get(
            "operations",
            params={
                "from": date_from.strftime('%Y-%m-%d') + "T09:00:00+03:00",
                "to": date_to.strftime('%Y-%m-%d') + "T09:00:00+03:00",
                "figi": figi,
            },
        )
        if res.status_code != 200:
            print(res.status_code, res.text)
            raise ValueError("Can't get operations list")

        return res.json()['payload']['operations']

    def search_by_figi(self, figi):
        if figi not in self._figi_cache:
            val = self.get(
                "market/search/by-figi", params={"figi": figi}
            ).json()['payload']
            if val['ticker'] in self.known_tickers:
                val['ticker'] = self.known_tickers[val['ticker']]
            self._figi_cache[figi] = val
        return self._figi_cache[figi]

    def search_last_op(self, date_to, days_back=60, op_type='Sell', figi=None):
        date_from = date_to - timedelta(days=days_back)
        if not isinstance(op_type, (list, tuple)):
            op_type = (op_type,)
        operations = self.operations(date_from, date_to, figi=figi)
        for op in operations:
            if op["operationType"] in op_type:
                return op

    def list_operations(self, date_from, date_to, group=False):
        operations = self.operations(date_from, date_to)

        last_usd_sell = None
        groups = {}

        print("\t".join(["Ticker", "Name", "Date", "Quantity", "Sum",
                         "Currency", "Sum (USD)"]))

        for op in reversed(operations):
            if op['status'] == "Decline":
                continue

            if op["operationType"] in ("PayIn", "PayOut"):
                continue

            ticker, name, date, quantity, summ, currency = (
                '', op["operationType"], op['date'].split('T')[0],
                0, op['payment'], op['currency'])

            if name in ("Buy", "BuyCard", "Sell"):
                figi = self.search_by_figi(op['figi'])
                quantity = op['quantity'] * (-1 if name == 'Sell' else 1)
                ticker = figi['ticker']
                name = figi['name']

                if (op["operationType"], figi['ticker']) == ("Sell", "USD"):
                    last_usd_sell = op
            
            elif name in ("BrokerCommission",):
                figi = self.search_by_figi(op['figi'])
                ticker = figi['ticker']            

            elif name in ("Dividend", "TaxDividend"):
                figi = self.search_by_figi(op['figi'])
                ticker = figi['ticker']
                name = figi['name'] + f" ({op['operationType']})"

            elif op["operationType"] in ("Tax", "TaxBack"):
                ticker = "$TAX"

            elif op['operationType'] in ("ServiceCommission",):
                ticker = "$COM"

            else:  # unknown
                print(json.dumps(op, indent=2))
                continue

            summ_usd = summ
            if currency == 'RUB':
                if last_usd_sell is None:
                    last_usd_sell = self.search_last_op(
                        date_from, figi=self.known_figis["USD"])
                summ_usd = round(summ / last_usd_sell['price'], 2)

            if group:
                params = groups.setdefault((ticker, name, currency),
                                           [date, 0, 0, 0])
                params[1] += quantity
                params[2] += summ
                params[3] += summ_usd
            else:
                self._echo_line(ticker, name, date, quantity, summ,
                                currency, summ_usd)
        
        if group:
            for ((ticker, name, currency),
                 (date, quantity, summ, summ_usd)) in groups.items():
                self._echo_line(ticker, name, date, quantity, summ,
                                currency, summ_usd)

    @staticmethod
    def _echo_line(ticker, name, date, quantity, summ, currency, summ_usd):
        if not quantity:
            quantity = ''
        print("\t".join([
            ticker, name, date, str(quantity),
            f"{summ:0.2f}", currency, f"{summ_usd:0.2f}"
        ]))
