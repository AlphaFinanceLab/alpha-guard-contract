import time
import os
import requests
from brownie import accounts, SimplePricer


URL = 'https://api.coingecko.com/api/v3/coins/markets?ids=ethereum&vs_currency=usd'


def get_eth_px():
    return int(requests.get(URL).json()[0]['current_price'] * 2**112)


def main():
    feeder = accounts.load('feeder')
    pricer = SimplePricer.at(os.getenv('PRICER_ADDRESS'))
    while True:
        try:
            pricer.setPrice(get_eth_px(), {'from': feeder, 'gasPrice': '1 gwei'})
        except Exception:
            pass
        time.sleep(60)
