from brownie.network.account import Account as _Account
from brownie.network.account import Accounts

class Account(object):

    def __init__(self, mnemonic:str):
        self._mnemonic = mnemonic

    def getBrownieAccount(self, accountNo:int) -> _Account:
        return Accounts().from_mnemonic(
            self._mnemonic, 
            count=1, 
            offset=accountNo)
