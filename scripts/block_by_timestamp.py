# source
# https://github.com/ethereum/web3.py/issues/1872 

# from web3.middleware import geth_poa_middleware
# from datetime import datetime
# from web3 import Web3
# import config

# web3 = Web3(Web3.HTTPProvider(config.rpc_url))
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)

from datetime import datetime
from brownie import web3

def getLatestBlockTimestamp():
    latestBlock = web3.eth.get_block('latest')
    latestBlockTimestamp = latestBlock.timestamp

    return latestBlockTimestamp

def getAverageBlockTime():
    currentBlock = web3.eth.get_block('latest')
    thenBlock = web3.eth.get_block(web3.eth.block_number - 500)

    return float((currentBlock.timestamp - thenBlock.timestamp) / 500.0)


def estimateBlockNrByTimestamp(timestamp):
    latestBlockTimestamp = getLatestBlockTimestamp()
    average_time = latestBlockTimestamp - timestamp
    if average_time < 0: raise ValueError('timestamp given by you exceed current block timestamp!')
    average_block = average_time / getAverageBlockTime()

    return int(web3.eth.blockNumber - average_block)


def getBlockNrForTimestamp(timestamp):
    block_nr = estimateBlockNrByTimestamp(timestamp)

    timestamp_found = web3.eth.get_block(block_nr)['timestamp'] 
    if timestamp_found == timestamp:
        print('{} MATCH'.format(block_nr))
        return block_nr

    average_block_time = getAverageBlockTime()
    delta_blocks = getDeltaBlocks(timestamp_found, timestamp, average_block_time)

    while abs(delta_blocks) > 0:
        block_nr += delta_blocks
        timestamp_found = web3.eth.get_block(block_nr)['timestamp']

        if timestamp_found == timestamp:
            print('{} MATCH'.format(block_nr))
            return block_nr

        dt = datetime.fromtimestamp(timestamp_found)
        delta_blocks = getDeltaBlocks(timestamp_found, timestamp, average_block_time)
        print('{} CHECKING {} ({}) target {} next delta {}'.format(
            block_nr,
            timestamp_found,
            dt.strftime('%b-%d-%Y %I:%M:%S %p %Z'),
            timestamp,
            delta_blocks))

def getDeltaBlocks(timestamp_found, timestamp_target, average_block_time):
    return int(-(timestamp_found - timestamp_target)/average_block_time)


hours_24_ago = datetime.utcnow().timestamp() - 24 * 60 * 60
print(hours_24_ago) #1644892963.530618

block_24_ago = estimateBlockNrByTimestamp(hours_24_ago)
print(block_24_ago) # Block: 15265950

blockInfo = web3.eth.get_block(block_24_ago)
print(blockInfo.timestamp) #1644893303