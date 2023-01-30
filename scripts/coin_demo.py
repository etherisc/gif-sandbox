from brownie import accounts

from scripts.util import get_package

def deploy_coin():
    gif = get_package('gif-contracts')
    coin = gif.TestCoin.deploy({'from':accounts[0]})
    return coin

def main():
    coin = deploy_coin()

    print('coin {}'.format(coin))
    print('coin.symbol() {}'.format(coin.symbol()))
    print('coin.balanceOf(accounts[0]) {}'.format(coin.balanceOf(accounts[0])))
