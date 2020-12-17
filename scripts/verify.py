import os
import requests


def main():
    print(requests.post('https://api-kovan.etherscan.io/api', json={
        'apikey': os.getenv('ETHERSCAN_TOKEN'),
        'module': 'contract',
        'action': 'verifysourcecode',
        # 'contractaddress': '',
        'codeformat': 'solidity-standard-json-input',
        # 'contractname': '',
        'compilerversion': 'v0.6.12+commit.27d51765',

    }).json())
    pass
