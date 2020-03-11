import json
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
        self._figi_store = {}

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.api_base or '', url)
        kwargs.setdefault('timeout', self.default_timeout)
        return super().request(method, url, *args, **kwargs)

    def get_figi(self, figi):
        if figi not in self._figi_store:
            val = self.get(
                "market/search/by-figi", data={"figi": figi}
            ).json()['payload']
            if val['ticker'] in self.known_tickers:
                val['ticker'] = self.known_tickers[val['ticker']]
            self._figi_store[figi] = val
        return self._figi_store[figi]

    def search_last_usd_sell(self, date_to):
        date_from = "2020-02-01"
        res = self.get(
            "operations",
            data={
                "from": date_from + "T00:00:00+00:00",
                "to": date_to + "T00:00:00+00:00",
                "figi": self.known_figis["USD"],
            },
        )
        if res.status_code != 200:
            print(res.status_code, res.text)
            return

        operations = res.json()['payload']['operations']
        for op in operations:
            if op["operationType"] == "Sell":
                return op

    def list_operations(self):
        date_from = "2020-03-01"
        date_to = "2021-04-01"
        res = self.get(
            "operations",
            data={
                "from": date_from + "T00:00:00+00:00",
                "to": date_to + "T00:00:00+00:00",
            },
        )
        if res.status_code != 200:
            print(res.status_code, res.text)
            return

        operations = res.json()['payload']['operations']

        line = "\t".join
        last_usd_sell = None

        print(line(["Ticker", "Name", "Date", "Quantity", "Sum",
                    "Currency", "Sum (USD)"]))

        for op in reversed(operations):
            if op['status'] == "Decline":
                continue

            if op["operationType"] in ("PayIn", "PayOut"):
                continue

            ticker, name, date, quantity, summ, currency = (
                '', op["operationType"], op['date'].split('T')[0],
                '', op['payment'], op['currency'])

            if name in ("Buy", "BuyCard", "Sell"):
                figi = self.get_figi(op['figi'])
                quantity = str(op['quantity'] * (-1 if name == 'Sell' else 1))
                ticker = figi['ticker']
                name = figi['name']

                if (op["operationType"], figi['ticker']) == ("Sell", "USD"):
                    last_usd_sell = op
            
            elif name in ("BrokerCommission",):
                figi = self.get_figi(op['figi'])
                ticker = figi['ticker']            

            elif name in ("Dividend", "TaxDividend"):
                figi = self.get_figi(op['figi'])
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
                    last_usd_sell = self.search_last_usd_sell(date_from)
                summ_usd = round(summ / last_usd_sell['price'], 2)
            print(line([ticker, name, date, quantity,
                        str(summ), currency, str(summ_usd)]))
