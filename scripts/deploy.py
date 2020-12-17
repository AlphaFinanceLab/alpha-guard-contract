import requests
from brownie import accounts, MockERC20, GuardToken, SimplePricer

URL = 'https://api.coingecko.com/api/v3/coins/markets?ids=ethereum&vs_currency=usd'


def get_eth_px():
    return int(requests.get(URL).json()[0]['current_price'] * 100) * 10**16


def main():
    deployer = accounts.load('deployer')
    token = MockERC20.deploy('MOCK ETH', 'mETH', {'from': deployer})
    pricer = SimplePricer.deploy(get_eth_px(), {'from': deployer})
    guard = GuardToken.deploy(token, pricer, 'MOCK GUARD', 'mGUARD', {'from': deployer})
