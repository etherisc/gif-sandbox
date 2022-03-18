from web3 import Web3

from brownie import (
    Contract,
    HelloWorldInsurance,
    InstanceHelper,
    interface
)

def s2b32(text: str):
    return '{:0<66}'.format(Web3.toHex(text.encode('ascii')))

def getInstanceOperatorService(gif: InstanceHelper) -> interface.IInstanceOperatorService:
    return getContractObject(interface.IInstanceOperatorService, gif.getInstanceOperatorService())

def getOracleOwnerService(gif: InstanceHelper) -> interface.IOracleOwnerService:
    return getContractObject(interface.IOracleOwnerService, gif.getOracleOwnerService())

def getHelloWorldProduct(address):
    return getContractObject(HelloWorldInsurance, address)

def getContractObject(contract, address):
    return Contract.from_abi(contract._name, address, contract.abi)