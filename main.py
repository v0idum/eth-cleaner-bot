import os
import time

from dotenv import load_dotenv
from loguru import logger
from web3 import Web3, HTTPProvider

from utils import current_datetime

load_dotenv('testing/.env')

VERSION = '2021-09-24'
START_TIME = current_datetime()

BONUS_GAS = 10000
BONUS_GAS_PRICE = Web3.toWei(2, 'gwei')


ENDPOINT_URL = os.getenv('ENDPOINT_URL')

GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT')

REPORTED_TODAY = False
REPORT_HOUR = 12

logger.add('eth.log', format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

# with open('intro.txt', 'r+') as f:
#     data = []
#     for line in f:
#         data.append(line.strip())     TODO get back
#     f.seek(0)
#     f.write('0000000000000\n' * 2)
#     f.truncate()

global WEB3, PRIVATE_KEY, ADDRESS_FROM, ADDRESS_TO, balance
CHAIN_ID = int(os.getenv('CHAIN_ID'))


def _get_balance():
    return WEB3.eth.getBalance(ADDRESS_FROM)


def transfer_eth(value):
    pass


def wait_for_deposit(poll_interval):
    logger.info('Deposit Waiting')
    while True:
        current_balance = _get_balance()
        if current_balance > balance:
            transfer_eth(current_balance)
        time.sleep(poll_interval)


def main():
    global WEB3, PRIVATE_KEY, ADDRESS_FROM, ADDRESS_TO
    WEB3 = Web3(HTTPProvider(ENDPOINT_URL))

    # PRIVATE_KEY = data[0] TODO get back
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    ADDRESS_FROM = WEB3.eth.account.from_key(PRIVATE_KEY).address
    # ADDRESS_TO = Web3.toChecksumAddress(data[1]) TODO get back
    ADDRESS_TO = Web3.toChecksumAddress(os.getenv('ADDRESS_TO'))

    print(_get_balance())

if __name__ == '__main__':
    main()
