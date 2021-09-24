from datetime import datetime, timezone, timedelta

import requests

ETH_USD_PRICE_API = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
SGP_TZ = timezone(timedelta(hours=8))
FORMAT = '%Y-%m-%d %H:%M:%S'


def _get_eth_price():
    return requests.get(ETH_USD_PRICE_API).json()['ethereum']['usd']


def eth_to_usd(eth_amount) -> str:
    return format(float(eth_amount) * _get_eth_price(), '.2f')


def current_datetime():
    return datetime.now(tz=SGP_TZ)


def now(fmt=None) -> str:
    return datetime.now(tz=SGP_TZ).strftime(FORMAT) if fmt is None else datetime.now(tz=SGP_TZ).strftime(fmt)


def current_hour() -> int:
    return datetime.now(tz=SGP_TZ).hour


def crop_key(key: str) -> str:
    return key[:4] + "...." + key[-4:]
