from brownie.network.account import Account

from brownie import (
    InstanceHelper,
    interface,
)

from scripts.util import getContract

class Instance(object):

    def __init__(self, registryAddress: Account, owner: Account):
        gif = InstanceHelper.deploy(
            registryAddress, 
            {'from': owner})
        
        self.ios = getContract(interface.IInstanceOperatorService, gif.getInstanceOperatorService())
        self.oos = getContract(interface.IOracleOwnerService, gif.getOracleOwnerService())
        self.instance = gif
        self.owner = owner
    
    @property
    def instanceOperatorService(self) -> interface.IInstanceOperatorService:
        return self.ios
    
    @property
    def oracleOwnerService(self) -> interface.IOracleOwnerService:
        return self.oos
    
    @property
    def contract(self) -> InstanceHelper:
        return self.instance

