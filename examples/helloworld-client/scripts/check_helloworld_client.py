from typing import Dict, List

from brownie import Contract, interface, network, Wei
from brownie.network import accounts
from brownie.network.account import Account

HELLOWORLD_CONTRACT_ADDRESS = '0x774DDa3beEf9650473549Be4EE7054a2ef5B0140'
HELLOWORLD_ACCOUNTS_MNEMONIC = 'candy maple cake sugar pudding cream honey rich smooth crumble sweet treat'

def load_event_facade() -> interface.IEventFacade:
    return Contract.from_abi(interface.IEventFacade._name, HELLOWORLD_CONTRACT_ADDRESS, interface.IEventFacade.abi)

def get_contract_object() -> interface.IHelloWorldFacade:
    return Contract.from_abi(interface.IHelloWorldFacade._name, HELLOWORLD_CONTRACT_ADDRESS, interface.IHelloWorldFacade.abi)

def get_account(hd_account_offset: int) -> Account:
    return accounts.from_mnemonic(
        HELLOWORLD_ACCOUNTS_MNEMONIC,
        count=1,
        offset=hd_account_offset)

def print_events(tx):
    output = []

    i = 0
    for event, params in tx.events.items():
        output.append('event[{}] {}'.format(i, event))
        i += 1

        for param, value in params.items():
            output.append('    {}: {}'.format(param, value))
    
    return '\n'.join(output)

def main():
    # make brownie load event definitions
    # only needed for event abi definitions for gif and oracle
    load_event_facade()

    hello_world = get_contract_object()
    customer_account = get_account(1)

    print('current network: {}'.format(network.show_active()))
    print('helloworld contract address: {}'.format(hello_world.address))
    print('customer account address: {}'.format(customer_account.address))

    print('\ncreating hello_world policy ...')
    premium = Wei("1.0 ether");
    policy_tx = hello_world.applyForPolicy({'from': customer_account, 'amount': premium})
    policy_id = policy_tx.return_value
    print('hello_world.applyForPolicy()\n    policyId {}'.format(policy_id))
    print('hello_world.applyForPolicy() tx events\n{}'.format(print_events(policy_tx)))

    print('\ncreating greeting claim ...')
    greeting = 'hey'
    greeting_tx = hello_world.greet(policy_id, greeting, {'from': customer_account})
    print('hello_world.greet() tx events\n{}'.format(print_events(greeting_tx)))
