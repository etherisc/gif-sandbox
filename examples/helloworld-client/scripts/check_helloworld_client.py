from typing import Dict

from brownie import Contract, interface, network
from brownie.network import accounts
from brownie.network.account import Account

from eth_event import get_topic_map, decode_logs

from web3 import Web3

HELLOWORLD_CONTRACT_ADDRESS = '0x3f6c622D32dA3BC70730C9E677ec343cb5acFe68'

HELLOWORLD_ACCOUNTS_MNEMONIC = 'candy maple cake sugar pudding cream honey rich smooth crumble sweet treat'
HELLOWORLD_DEPLOY_ACCOUNT_OFFSET = 1


def get_topics_map() -> Dict:
    topics_abi_file = open(TOPICS_ABI_FILE_NAME).read()
    return get_topic_map(topics_abi_file)

def get_contract_object() -> interface.IHelloWorldInsurance:
    return Contract.from_abi(interface.IHelloWorldInsurance._name, HELLOWORLD_CONTRACT_ADDRESS, interface.IHelloWorldInsurance.abi)

def get_account(hd_account_offset: int) -> Account:
    return accounts.from_mnemonic(
        HELLOWORLD_ACCOUNTS_MNEMONIC,
        count=1,
        offset=hd_account_offset)

def get_deploy_account() -> Account:
    return get_account(HELLOWORLD_DEPLOY_ACCOUNT_OFFSET)

def print_event_topic(signature: str):
    signature_hex = Web3.toHex(Web3.keccak(text=signature))
    print('  sig {} -> topic {}'.format(signature, signature_hex))

def main():
    hello_world = get_contract_object()
    print(dir(hello_world))
    print(hello_world.topics)

    deploy_account = get_deploy_account()
    topic_map = get_topic_map(hello_world.abi)

    print('current network: {}'.format(network.show_active()))
    print('helloworld address: {}'.format(hello_world.address))

    premium = 100 * 10**16;
    policy_tx = hello_world.applyForPolicy({'from': deploy_account, 'amount': premium})
    policy_tx.wait(1)

    print('events to topic hashes: (manually ...)')
    print_event_topic('LogGreetingPolicyCreated(bytes32)')

    print_event_topic('LogMetadataStateChanged(bytes32,uint8)')
    print_event_topic('LogNewApplication(uint256,bytes32)')
    print_event_topic('LogApplicationStateChanged(bytes32,uint8)')
    print_event_topic('LogPolicyStateChanged(bytes32,uint8)')
    print_event_topic('LogNewPolicy(bytes32)')

    print('policy tx decoded logs:')
    for (idx, log) in enumerate(policy_tx.logs):
        print('log[{}], logIndex {}:'.format(idx, log['logIndex']))
        print('  address: {}'.format(log['address']))
        print('  topics[0]: {}'.format(log['topics'][0].hex()))
        # print('  data: {}'.format(log['data']))

    # print('policy tx.events: {}'.format(policy_tx.events))
    # print('policy tx.info(): {}'.format(policy_tx.info()))