import pytest

from brownie import (
    chain,
    interface,
    web3,
    UsdcPriceDataProvider,
    USD1,
)

from scripts.util import contract_from_address

MAINNET = 1
GANACHE = 1337
GANACHE2 = 1234

USDC_CONTACT_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
CHAINLINK_USDC_USD_FEED_MAINNET = '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6'


# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

# use the settings below to run this against mainnet
# brownie test tests/test_aggregator_usdc.py::test_live_data --interactive --network=mainnet-fork
def test_live_aggregator_interface_mainnet(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != MAINNET:
        print('test case only relevant when executed on mainnet')
        return

    assert usdc_feeder.isMainnetProvider()

    chainlink_aggregator = contract_from_address(
        interface.AggregatorV2V3Interface,
        usdc_feeder.getChainlinkAggregatorAddress())

    assert chainlink_aggregator.address == CHAINLINK_USDC_USD_FEED_MAINNET

    latest_round_data = chainlink_aggregator.latestRoundData().dict()
    round_id = latest_round_data['roundId']

    assert chainlink_aggregator.latestRound() == round_id
    assert chainlink_aggregator.latestAnswer() == latest_round_data['answer']
    assert chainlink_aggregator.latestTimestamp() == latest_round_data['startedAt']
    assert chainlink_aggregator.latestTimestamp() == latest_round_data['updatedAt']

    assert chainlink_aggregator.getAnswer(round_id) == latest_round_data['answer']
    assert chainlink_aggregator.getTimestamp(round_id) == latest_round_data['updatedAt']

    round_data = chainlink_aggregator.getRoundData(round_id).dict()
    assert round_data['answer'] == latest_round_data['answer']
    assert round_data['answeredInRound'] == latest_round_data['answeredInRound']
    assert round_data['roundId'] == latest_round_data['roundId']
    assert round_data['startedAt'] == latest_round_data['startedAt']
    assert round_data['updatedAt'] == latest_round_data['updatedAt']


def test_aggregator_interface_ganache(
    usdc_feeder: UsdcPriceDataProvider,
    usd1: USD1
):

    if web3.chain_id == MAINNET:
        print('test case only relevant when executed on testnet')
        return

    assert usdc_feeder.isTestnetProvider()

    multiplier = 10 ** usd1.decimals()
    price1 = int(1.0 * multiplier)
    price2 = int(0.999 * multiplier)
    price3 = int(1.01 * multiplier)

    timestamp = chain.time()
    usdc_feeder.addRoundData(price1, timestamp - 2)
    usdc_feeder.addRoundData(price2, timestamp - 1)
    usdc_feeder.addRoundData(price3, timestamp)

    chainlink_aggregator = contract_from_address(
        interface.AggregatorV2V3Interface,
        usdc_feeder.getChainlinkAggregatorAddress())

    assert chainlink_aggregator.address == usdc_feeder.address

    latest_round_data = chainlink_aggregator.latestRoundData().dict()
    round_id = latest_round_data['roundId']

    assert round_id == 3
    assert chainlink_aggregator.latestRound() == round_id
    assert chainlink_aggregator.latestAnswer() == latest_round_data['answer']
    assert chainlink_aggregator.latestTimestamp() == latest_round_data['startedAt']
    assert chainlink_aggregator.latestTimestamp() == latest_round_data['updatedAt']

    assert chainlink_aggregator.getAnswer(round_id) == latest_round_data['answer']
    assert chainlink_aggregator.getTimestamp(round_id) == latest_round_data['updatedAt']

    # verify latest round data via explicit round id
    round_data = chainlink_aggregator.getRoundData(round_id).dict()
    assert round_data['answer'] == latest_round_data['answer']
    assert round_data['answeredInRound'] == latest_round_data['answeredInRound']
    assert round_data['roundId'] == latest_round_data['roundId']
    assert round_data['startedAt'] == latest_round_data['startedAt']
    assert round_data['updatedAt'] == latest_round_data['updatedAt']

    # check middle data
    round_id2 = 2
    timestamp2 = timestamp - 1
    assert chainlink_aggregator.getAnswer(round_id2) == price2
    assert chainlink_aggregator.getTimestamp(round_id2) == timestamp2

    round_data2 = chainlink_aggregator.getRoundData(round_id2).dict()
    assert round_data2['answer'] == price2
    assert round_data2['answeredInRound'] == round_id2
    assert round_data2['roundId'] == round_id2
    assert round_data2['startedAt'] == timestamp2
    assert round_data2['updatedAt'] == timestamp2
