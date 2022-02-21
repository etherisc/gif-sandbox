from typing import Dict

from brownie import Wei
from brownie.network import accounts
from brownie.network.account import Account

ACCOUNTS_MNEMONIC = 'candy maple cake sugar pudding cream honey rich smooth crumble sweet treat'

def get_account(hd_account_offset: int) -> Account:
    return accounts.from_mnemonic(
        ACCOUNTS_MNEMONIC,
        count=1,
        offset=hd_account_offset)

def print_balances(accounts: Dict):
    for account_name, account in accounts.items():
        print('{}: {:.3f} ETH'.format(account_name, Wei(account.balance()).to("ether")))

def main():
    account1 = get_account(1)
    account2 = get_account(2)
    # account1 = accounts[0]
    # account2 = accounts[1]

    print('account balances before transfer')
    print_balances({'account1': account1, 'account2': account2})

    account1.transfer(account2, "1 ether")
    print('account balances after 1st transfer')
    print_balances({'account1': account1, 'account2': account2})

    account1.transfer(account2, "1 ether")
    print('account balances after 2nd transfer')
    print_balances({'account1': account1, 'account2': account2})

    account1.transfer(account2, "1 ether")
    print('account balances after 3rd transfer')
    print_balances({'account1': account1, 'account2': account2})
