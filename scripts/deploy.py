import time
import os
import requests
import subprocess
from brownie import accounts, MockERC20, GuardToken, SimplePricer, UniswapILPricer


URL = 'https://api.coingecko.com/api/v3/coins/markets?ids=ethereum&vs_currency=usd'


def get_eth_px():
    return int(requests.get(URL).json()[0]['current_price'] * 2**112)


# def deploy(contract, name, deployer, *args):
#     result = contract.deploy(*args, {'from': deployer})
#     time.sleep(10)  # Wait a bit to ensure Etherscan picks it up
#     subprocess.check_call([
#         'solt',
#         'verify',
#         'solc-input-contracts.json',
#         result.address,
#         name,
#         '--compiler',
#         'v0.6.12',
#         '--etherscan',
#         os.getenv('ETHERSCAN_TOKEN'),
#         '--infura',
#         os.getenv('WEB3_INFURA_PROJECT_ID'),
#         '--network',
#         'kovan',
#     ])
#     return result


# def main():
#     subprocess.check_call(['solt', 'write', 'contracts', '--npm'])
#     deployer = accounts.load('deployer')
#     feeder = accounts.load('feeder')
#     token = deploy(MockERC20, 'MockERC20', deployer, 'Mock ETH', 'mETH')
#     pricer = deploy(SimplePricer, 'SimplePricer', deployer, get_eth_px())
#     pricer.transferOwnership(feeder, {'from': deployer})
#     guard = deploy(GuardToken, 'GuardToken', deployer, token, pricer, 'MOCK GUARD', 'mGUARD')


def main():
    subprocess.check_call(['solt', 'write', 'contracts', '--npm'])
    deployer = accounts.load('deployer')
    feeder = accounts.load('feeder')
    token = MockERC20.deploy('UNI V2 WETH-DAI', 'UNI V2 ETH-DAI', {'from': deployer})
    simple = SimplePricer.deploy(get_eth_px(), {'from': deployer})
    simple.setRelayer(feeder, {'from': deployer})
    pricer = UniswapILPricer.deploy(
        simple,
        5*10**16,
        [86400, 3*86400, 7*86400, 14*86400],
        [1*10**18, 2*10**18, 3*10**18, 4*10**18],
        {'from': deployer},
    )
    guard = GuardToken.deploy(
        token,
        pricer,
        'GUARD_UNI_V2_WETH_DAI',
        'GUARD_UNI_V2_WETH_DAI',
        {'from': deployer},
    )
