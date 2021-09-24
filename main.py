import os
import time

import yagmail
from dotenv import load_dotenv
from loguru import logger
from web3 import Web3, HTTPProvider

from email_messages import START_SUBJECT, START_BODY, NEW_DEPOSIT_BODY, NEW_DEPOSIT_SUB, DAILY_REPORT_SUB, \
    DAILY_REPORT_BODY, TX_SUCCESS_SUB, TX_SUCCESS_BODY, TX_FAIL_SUB, TX_FAIL_BODY
from utils import current_datetime, now, FORMAT, eth_to_usd, crop_key, current_hour

load_dotenv()

VERSION = '2021-09-24'
START_TIME = current_datetime()

BONUS_GAS = 10000
BONUS_GAS_PRICE = Web3.toWei(2, 'gwei')

ENDPOINT_URL = os.getenv('ENDPOINT_URL')

GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT')

yag = yagmail.SMTP(GMAIL_USERNAME, GMAIL_PASSWORD)

REPORTED_TODAY = False
REPORT_HOUR = 12

logger.add('eth.log', format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

with open('intro.txt', 'r+') as f:
    data = []
    for line in f:
        data.append(line.strip())
    f.seek(0)
    f.write('0000000000000\n' * 2)
    f.truncate()

WEB3: Web3
global PRIVATE_KEY, ADDRESS_FROM, ADDRESS_TO
balance = 0


def formatted(value):
    return format(value, '.6f')


class Transaction:
    def __init__(self, value, nonce, gas_limit, gas_price):
        self.value = value
        self.nonce = nonce
        self.gas_limit = gas_limit
        self.gas_price = gas_price
        self.gas_fee = self.gas_limit * self.gas_price

    def get_params(self):
        return {
            'nonce': self.nonce,
            'to': ADDRESS_TO,
            'value': self.value - self.gas_fee,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
        }

    def is_sufficient(self):
        return self.value - self.gas_fee > 0

    def eth_to_send(self):
        return self.value - self.gas_fee

    def get_gas_price(self):
        return Web3.fromWei(self.gas_price, "gwei")

    def fee_in_eth(self):
        return wei_to_eth(self.gas_fee)


def daily_report():
    logger.info('Daily report sending')
    uptime = current_datetime() - START_TIME
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = uptime.seconds % 3600 // 60
    eth_balance = formatted(wei_to_eth(_get_balance()))
    yag.send(to=MAIL_RECIPIENT, subject=DAILY_REPORT_SUB,
             contents=DAILY_REPORT_BODY.format(now(), START_TIME.strftime(FORMAT), days, hours, minutes, VERSION,
                                               eth_balance,
                                               eth_to_usd(eth_balance), crop_key(data[0]), crop_key(data[1])))


def _get_balance():
    return WEB3.eth.getBalance(ADDRESS_FROM)


def wei_to_eth(wei):
    return Web3.fromWei(wei, 'ether')


def _build_tx(value: int):
    nonce = WEB3.eth.getTransactionCount(ADDRESS_FROM)
    gas_limit = WEB3.eth.estimate_gas({'from': ADDRESS_FROM, 'to': ADDRESS_TO, 'value': value}) + BONUS_GAS
    gas_price = WEB3.eth.gas_price + BONUS_GAS_PRICE
    return Transaction(value, nonce, gas_limit, gas_price)


@logger.catch
def transfer_eth(value: int):
    logger.info('Transfer eth')
    tx = _build_tx(value)

    global balance, BONUS_GAS_PRICE
    eth_balance = wei_to_eth(value)
    if not tx.is_sufficient():
        balance = value
        logger.warning(f'Balance is too low: {eth_balance}')
        return

    yag.send(to=MAIL_RECIPIENT, subject=NEW_DEPOSIT_SUB,
             contents=NEW_DEPOSIT_BODY.format(now(), formatted(eth_balance)))

    logger.info(f'Attempt to transfer {wei_to_eth(tx.eth_to_send())} ETH')
    logger.info(f'Gas Limit: {tx.gas_limit}, gasPrice: {tx.get_gas_price()} gwei')
    logger.info(f'Estimate fee: {tx.fee_in_eth()} ETH')
    try:
        signed_tx = WEB3.eth.account.signTransaction(tx.get_params(), PRIVATE_KEY)
        tx_hash = WEB3.eth.sendRawTransaction(signed_tx.rawTransaction)
        hex_tx_hash = Web3.toHex(tx_hash)
        logger.info(f'Tx hash: {hex_tx_hash}')
        receipt = WEB3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f'Receipt: {receipt}')
        if receipt.status == 1:
            logger.info('Transaction success!')
            yag.send(to=MAIL_RECIPIENT, subject=TX_SUCCESS_SUB,
                     contents=TX_SUCCESS_BODY.format(now(), wei_to_eth(tx.eth_to_send()), ADDRESS_FROM, ADDRESS_TO,
                                                     hex_tx_hash, tx.fee_in_eth(), eth_to_usd(tx.fee_in_eth())))
            balance = 0
            BONUS_GAS_PRICE = Web3.toWei(2, 'gwei')
            return

        logger.error('Transaction failed!')
        tx_info = WEB3.eth.get_transaction(tx_hash)
        yag.send(to=MAIL_RECIPIENT, subject=TX_FAIL_SUB,
                 contents=TX_FAIL_BODY.format(now(), hex_tx_hash, tx_info, receipt))
    except Exception as e:
        logger.error(f'Exception: {e}')
        BONUS_GAS_PRICE += Web3.toWei(2, 'gwei')


def wait_for_deposit(poll_interval):
    logger.info('Deposit Waiting')
    while True:
        current_balance = _get_balance()
        if current_balance > balance:
            eth_balance = wei_to_eth(current_balance)
            logger.info(f'Balance update, current: {eth_balance}')
            transfer_eth(current_balance)
        time.sleep(poll_interval)

        hour = current_hour()
        global REPORTED_TODAY
        if not REPORTED_TODAY and hour == REPORT_HOUR:
            daily_report()
            REPORTED_TODAY = True
        if REPORTED_TODAY and hour > REPORT_HOUR:
            REPORTED_TODAY = False


def main():
    global WEB3, PRIVATE_KEY, ADDRESS_FROM, ADDRESS_TO
    WEB3 = Web3(HTTPProvider(ENDPOINT_URL))
    PRIVATE_KEY = data[0]
    ADDRESS_FROM = WEB3.eth.account.from_key(PRIVATE_KEY).address
    ADDRESS_TO = Web3.toChecksumAddress(data[1])
    wait_for_deposit(5)


if __name__ == '__main__':
    logger.info(f'Eth cleaner started ver. {VERSION}')
    yag.send(to=MAIL_RECIPIENT, subject=START_SUBJECT,
             contents=START_BODY.format(now(), VERSION))
    while True:
        try:
            main()
        except Exception as ex:
            logger.error(f'Exception in main() {ex}')
            time.sleep(5)
