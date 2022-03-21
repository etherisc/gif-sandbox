from web3 import Web3
from brownie import Contract

def s2b32(text: str):
    return '{:0<66}'.format(Web3.toHex(text.encode('ascii')))

def getContract(contract, address):
    return Contract.from_abi(contract._name, address, contract.abi)