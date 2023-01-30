from web3 import Web3

from brownie import (
    Contract, 
)


def contract_from_address(contractClass, contractAddress):
    return Contract.from_abi(contractClass._name, contractAddress, contractClass.abi)

from brownie import accounts, config, project
from brownie.convert import to_bytes
from brownie.network.account import Account

CONFIG_DEPENDENCIES = 'dependencies'

def s2h(text: str) -> str:
    return Web3.toHex(text.encode('ascii'))

def h2s(hex: str) -> str:
    return Web3.toText(hex).split('\x00')[-1]

def h2sLeft(hex: str) -> str:
    return Web3.toText(hex).split('\x00')[0]

def s2b32(text: str):
    return '{:0<66}'.format(Web3.toHex(text.encode('ascii')))[:66]

def b322s(b32: bytes):
    return b32.decode().split('\x00')[0]

def s2b(text:str):
    return s2b32(text)

def b2s(b32: bytes):
    return b322s(b32)

def keccak256(text:str):
    return Web3.solidityKeccak(['string'], [text]).hex()

def get_account(mnemonic: str, account_offset: int) -> Account:
    return accounts.from_mnemonic(
        mnemonic,
        count=1,
        offset=account_offset)

def get_package(substring: str):
    for dependency in config[CONFIG_DEPENDENCIES]:
        if substring in dependency:
            print("using package '{}' for '{}'".format(
                dependency,
                substring))
            
            return project.load(dependency, raise_if_loaded=False)
    
    print("no package for substring '{}' found".format(substring))
    return None

# source: https://github.com/brownie-mix/upgrades-mix/blob/main/scripts/helpful_scripts.py 
def encode_function_data(*args, initializer=None):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if not len(args): args = b''

    if initializer: return initializer.encode_input(*args)

    return b''
