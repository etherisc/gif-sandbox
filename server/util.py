import logging

from brownie.network.web3 import Web3
from brownie import Contract, web3

def s2b32(text: str):
    return '{:0<66}'.format(Web3.toHex(text.encode('ascii')))

def getContract(contract, address):
    return Contract.from_abi(contract._name, address, contract.abi)

def getWeb3Contract(contract, address):
    return web3.eth.contract(address, abi=contract.abi)