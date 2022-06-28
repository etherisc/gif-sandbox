from web3 import Web3
from brownie import Contract, interface

def s2b(text:str):
    return '{:0<66}'.format(Web3.toHex(text.encode('ascii')))

def b2s(b32: bytes):
    return b32.decode().split('\x00')[0]

def getInstanceService(registryAddress):
    registry = getContract(interface.IRegistry, registryAddress)
    return getContract(interface.IInstanceService, registry.getContract(s2b('InstanceService')))

def getContract(contract, address):
    return Contract.from_abi(contract._name, address, contract.abi)