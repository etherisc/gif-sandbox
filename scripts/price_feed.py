# initial sources from https://docs.chain.link/docs/data-feeds/price-feeds/
# question regarding data feed switch https://ethereum.stackexchange.com/questions/114835/read-all-historical-price-data-of-a-chainlink-price-feed-in-javascript/138131#138131

import argparse
import sys

from dotenv import dotenv_values
from web3 import Web3

# RPC endpoint URLs
rpcEndpoint = {}

# see https://ethereumnodes.com/
rpcEndpoint['mainnet'] = 'https://rpc.flashbots.net/'
rpcEndpoint['goerli'] = 'https://rpc.ankr.com/eth_goerli'

# Price Feed addresses from https://docs.chain.link/docs/data-feeds/price-feeds/addresses/?network=ethereum
feedAddress = {}

feedAddress['mainnet'] = {}
feedAddress['mainnet']['USDC/USD'] = '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6'
feedAddress['mainnet']['USDT/USD'] = '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D'
feedAddress['mainnet']['USDN/USD'] = '0x7a8544894F7FD0C69cFcBE2b4b2E277B0b9a4355'

feedAddress['mainnet']['USDP/USD'] = '0x09023c0DA49Aaf8fc3fA3ADF34C6A7016D38D5e3'
feedAddress['mainnet']['TUSD/USD'] = '0xec746eCF986E2927Abd291a2A1716c940100f8Ba'

feedAddress['goerli'] = {}
feedAddress['goerli']['BTC/USD'] = '0xA39434A63A52E749F02807ae27335515BA4b07F7'

# AggregatorV3Interface ABI
abiFeed = '[{"inputs":[{"internalType":"uint16","name":"phaseId","type":"uint16"}],"name":"phaseAggregators","outputs":[{"internalType":"address","name":"address","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRound","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"phaseId","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
abiAggregator = '[{"inputs":[],"name":"latestRound","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

def getWeb3(net):
    if net not in rpcEndpoint:
        print('no rpc endpoint for net={}'.format(net))
        exit(-1)

    return Web3(Web3.HTTPProvider(rpcEndpoint[net]))


def getFeed(net, pair):
    web3 = getWeb3(net)

    if net not in feedAddress:
        print('no feeds defined for net={}'.format(net))
        exit(-2)

    if pair not in feedAddress[net]:
        print('no feeds defined for net={} and pair={}'.format(net, pair))
        exit(-3)

    addr = feedAddress[net][pair]

    return web3.eth.contract(address=addr, abi=abiFeed)


def getAggregator(web3, aggregatorAddress):
    return web3.eth.contract(address=aggregatorAddress, abi=abiAggregator)


def getAggregators(feed):
    aggregators = []

    phaseId = feed.functions.phaseId().call()
    for i in range(1, phaseId + 1):
        aggregatorAddress = feed.functions.phaseAggregators(i).call()
        aggregators.append((i, aggregatorAddress))

    return aggregators


def fetchAggregatorData(feed, phaseId, latestRound):
    roundIdBase = phaseId * 2**64

    print('# roundId answer startedAt updatedAt answeredInRound phaseId aggregatorRoundId')
    for aggregatorRoundId in range(1, latestRound + 1):
        roundId = roundIdBase + aggregatorRoundId
        data = feed.functions.getRoundData(roundId).call()
        print(data[0], data[1], data[2], data[3], data[4], phaseId, aggregatorRoundId)


def configure():
    config = dotenv_values('.env')
    if 'RPC_MAINNET' in config:
        print('# using rpc endpoint RPC_MAINNET in .env')
        rpcEndpoint['mainnet'] = config['RPC_MAINNET']


def do(net, pair, trunc):
    feed = getFeed(net, pair)
    aggregators = getAggregators(feed)
    web3 = getWeb3(net)
    description = feed.functions.description().call()

    print('# net {} chainId {} feedAddress {} description "{}"'.format(net, web3.eth.chain_id, feed.address, description))

    for a in aggregators:
        phaseId, address = a
        aggregator = getAggregator(web3, address)
        
        try:
            print('# phaseId {} aggregatorAddress {}'.format(phaseId, address))
            version = aggregator.functions.version().call()
            latestRound = aggregator.functions.latestRound().call()
            print('# version {} latestRound {} trunc {}'.format(version, latestRound, trunc))

            # if truncate defined, set number of samples to min(latestRound, trunc)
            if trunc > 0 and latestRound > trunc:
                latestRound = trunc
            
            fetchAggregatorData(feed, phaseId, latestRound)

        except:
            exInfo = sys.exc_info()
            print('# exception {} {} {}'.format(exInfo[0], exInfo[1], exInfo[2]))


def main() -> int:
    parser = argparse.ArgumentParser(description='read chainlink price feed data.')
    parser.add_argument('--pair', type=str, help='pair, eg: USDC/USD, USDT/USD')
    parser.add_argument('--net', type=str, default='mainnet', help='net to connect, one of: goerli, mainnet')
    parser.add_argument('--trunc', type=int, default=0, help='truncate feed data after n samples per phase (default: 0 = disable truncate)')
    args = parser.parse_args()

    configure()
    do(args.net, args.pair, args.trunc)

    return 0


# example command lines for calling this script
# python scripts/price_feed.py --help
# python scripts/price_feed.py --pair USDC/USD --trunc 2
# python scripts/price_feed.py --net mainnet --pair USDC/USD > chainlink_usdc_usd_all.txt
if __name__ == '__main__':
    sys.exit(main())