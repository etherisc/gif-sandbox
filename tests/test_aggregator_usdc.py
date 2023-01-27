import brownie
import pytest

from brownie import (
    web3,
    UsdcPriceDataProvider,
    USD1,
)

from brownie.network.account import Account

MAINNET = 1
GANACHE = 1337
GANACHE2 = 1234

USDC_CONTACT_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
CHAINLINK_USDC_USD_FEED_MAINNET = '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6'

# actual chainlink aggregator data, may be validated against
# https://etherscan.io/address/0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6#readContract
USDC_CHAINLINK_DATA = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103823 100008784 1660383738 1660383738 36893488147419103823',
    '36893488147419103824 100000000 1660383820 1660383820 36893488147419103824',
    '36893488147419103825 99985387 1660470242 1660470242 36893488147419103825',
    '36893488147419103826 99989424 1660556656 1660556656 36893488147419103826',
    '36893488147419103827 100017933 1660643065 1660643065 36893488147419103827',
    '36893488147419103828 100007204 1660729494 1660729494 36893488147419103828',
    '36893488147419103829 100000000 1660815929 1660815929 36893488147419103829',
    '36893488147419103830 100002388 1660902349 1660902349 36893488147419103830',
    '36893488147419103831 100000554 1660988749 1660988749 36893488147419103831',
    '36893488147419103832 99990785 1661075158 1661075158 36893488147419103832',
]

# get same price feed response as before
USDC_CHAINLINK_DATA_PRICE_SEQUENCE_REPEAT = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
]

# miss/skip element in sequence of price feed responses
USDC_CHAINLINK_DATA_PRICE_SEQUENCE_SKIP = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103824 100008784 1660383738 1660383738 36893488147419103824',
]

# decrease element in sequence of price feed responses
USDC_CHAINLINK_DATA_PRICE_DECREASE = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103821 100008784 1660383738 1660383738 36893488147419103821',
]

# for usdc/usd quality promise by chainlink see https://docs.chain.link/data-feeds/price-feeds/addresses
# 'hacked' price feed to force heatbeat violation
# ie duration between consecuteve createdAt/updatedAt timestamps > 24h + margin
USDC_CHAINLINK_DATA_HEARTBEAT_VIOLATED = [
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103823 100008784 1660383807 1660383807 36893488147419103823',
    '36893488147419103824 100000000 1660470308 1660470308 36893488147419103824',
    '36893488147419103825 99985387 1660506308 1660506308 36893488147419103825',
]

# 'hacked' price feed to force deviation violation
# ie price difference between two rounds larger than 0.25%
USDC_CHAINLINK_DATA_DEVIATION_VIOLATED = [
    '36893488147419103822 100000017 1660297306 1660297306 36893488147419103822',
    '36893488147419103823 100260000 1660383738 1660383738 36893488147419103823',
    '36893488147419103824 100000000 1660383820 1660383820 36893488147419103824',
    '36893488147419103825 99985387 1660470242 1660470242 36893488147419103825',
]

# i createdAt  answer    comment
# 0 1660070000 100000017 normal
# 1 1660080000  99700000 below recovery but above trigger
# 2 1660090000  99500001 1 above trigger
# 3 1660100000  99500000 at trigger
# 4 1660120000  99800000 above trigger but below recovery
# 5 1660140000  98000000 really below trigger
# 6 1660160000  99899999 1 below recovery
# 7 1660186401  99900000 at recovery
# 8 1660200000  99700000 below recovery and above trigger
USDC_CHAINLINK_DATA_TRIGGER_AND_RECOVER = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660070000 1660070000 36893488147419103822',
    '36893488147419103823 99700000 1660080000 1660080000 36893488147419103823',
    '36893488147419103824 99500001 1660090000 1660090000 36893488147419103824',
    '36893488147419103825 99500000 1660100000 1660100000 36893488147419103825',
    '36893488147419103826 99800000 1660120000 1660120000 36893488147419103826',
    '36893488147419103827 98000000 1660140000 1660140000 36893488147419103827',
    '36893488147419103828 99899999 1660160000 1660160000 36893488147419103828',
    '36893488147419103829 99900000 1660186400 1660186400 36893488147419103829',
    '36893488147419103830 99700000 1660200000 1660200000 36893488147419103830',
]

# same as USDC_CHAINLINK_DATA_TRIGGER_AND_RECOVER just with streched timeline
# to ensure recovery takes longer than 24h
USDC_CHAINLINK_DATA_TRIGGER_AND_DEPEG = [
    # roundId             qnswer    startedAt  updatedAt  answeredInRound
    '36893488147419103822 100000017 1660070000 1660070000 36893488147419103822',
    '36893488147419103823 99700000 1660080000 1660080000 36893488147419103823',
    '36893488147419103824 99500001 1660090000 1660090000 36893488147419103824',
    '36893488147419103825 99500000 1660100000 1660100000 36893488147419103825',
    '36893488147419103826 99800000 1660120000 1660120000 36893488147419103826',
    '36893488147419103827 98000000 1660140000 1660140000 36893488147419103827',
    '36893488147419103828 99899999 1660160000 1660160000 36893488147419103828',
    '36893488147419103829 99900000 1660186401 1660186401 36893488147419103829',
    '36893488147419103830 99700000 1660200000 1660200000 36893488147419103830',
    '36893488147419103831 99990000 1660210000 1660210000 36893488147419103831',
]

EVENT_TYPE = {}
EVENT_TYPE['Undefined'] = 0 
EVENT_TYPE['Update'] = 1
EVENT_TYPE['TriggerEvent'] = 2
EVENT_TYPE['RecoveryEvent'] = 3
EVENT_TYPE['DepegEvent'] = 4

STATE_COMPLIANCE = {}
STATE_COMPLIANCE['Undefined'] = 0
STATE_COMPLIANCE['Initializing'] = 1
STATE_COMPLIANCE['Valid'] = 2
STATE_COMPLIANCE['FailedOnce'] = 3
STATE_COMPLIANCE['FailedMultipleTimes'] = 4

STATE_STABILITY = {}
STATE_STABILITY['Undefined'] = 0
STATE_STABILITY['Initializing'] = 1
STATE_STABILITY['Stable'] = 2
STATE_STABILITY['Triggered'] = 3
STATE_STABILITY['Depegged'] = 4

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_feeder_fixture(
    usdc_feeder: UsdcPriceDataProvider,
    usd1: USD1
):
    assert usdc_feeder.getDecimals() == 8
    assert usdc_feeder.getHeartbeat() == 24 * 3600
    assert usdc_feeder.getDeviation() == 0.0025 * 10**8

    if web3.chain_id == GANACHE or web3.chain_id == GANACHE2:
        assert usdc_feeder.isTestnetProvider()
        assert usdc_feeder.getAggregatorAddress() == usdc_feeder.address
        assert usdc_feeder.getToken() == usd1
    elif web3.chain_id == MAINNET:
        assert usdc_feeder.isMainnetProvider()
        assert usdc_feeder.getAggregatorAddress() == CHAINLINK_USDC_USD_FEED_MAINNET
        assert usdc_feeder.getToken() == USDC_CONTACT_ADDRESS
    else:
        print('ERROR chain_id {} not supported'.format(web3.chain_id))
        assert False


# use the settings below to run this against mainnet
# brownie test tests/test_aggregator_usdc.py::test_live_data --interactive --network=mainnet-fork
def test_live_data(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != MAINNET:
        print('test case only relevant when executed on mainnet')
        return

    assert usdc_feeder.isMainnetProvider()

    round_data = usdc_feeder.latestRoundData().dict()
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    print('round_data {}'.format(round_data))
    print('price_info {}'.format(price_info))

    assert round_data['startedAt'] > 0
    assert price_info['createdAt'] == 0

    new_info = usdc_feeder.hasNewPriceInfo().dict()
    print('new_info {}'.format(new_info))

    assert new_info['newInfoAvailable'] == True
    assert new_info['priceId'] == round_data['roundId']
    assert new_info['timeDelta'] == round_data['startedAt']

    usdc_feeder.processLatestPriceInfo()
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    print('price_info {}'.format(price_info))

    # test assumes that usdc feed is ok currently ...
    assert price_info['id'] == round_data['roundId']
    assert price_info['price'] == round_data['answer']
    assert price_info['compliance'] == STATE_COMPLIANCE['Initializing']
    assert price_info['stability'] == STATE_STABILITY['Stable']
    assert price_info['triggeredAt'] == 0
    assert price_info['depeggedAt'] == 0
    assert price_info['createdAt'] == round_data['updatedAt']

    # test assumes that now new round data has been made available since the last call
    new_info = usdc_feeder.hasNewPriceInfo().dict()
    print('new_info {}'.format(new_info))
    
    assert new_info['newInfoAvailable'] == False
    assert new_info['priceId'] == price_info['id']
    assert new_info['timeDelta'] == 0


def test_feed_manipulation_disabled_on_mainnet(
    usdc_feeder: UsdcPriceDataProvider,
    instanceOperator:Account,
    productOwner:Account,
):

    if web3.chain_id != MAINNET:
        print('test case only relevant when executed on mainnet')
        return

    assert usdc_feeder.isMainnetProvider()

    # check AggregatorDataProvider.setRoundData 
    with brownie.reverts("ERROR:ADP-001:NOT_TEST_CHAIN"):
        usdc_feeder.setRoundData(
            36893488147419104007,
            99994290,
            1671427679,
            1671427679,
            36893488147419104007,
            {'from':productOwner}
        )

    # check AggregatorDataProvider.setRoundData 
    with brownie.reverts("Ownable: caller is not the owner"):
        usdc_feeder.setRoundData(
            36893488147419104007,
            99994290,
            1671427679,
            1671427679,
            36893488147419104007,
            {'from':instanceOperator}
        )

    # check IPriceDataProvider.forceDepegForNextPriceInfo
    with brownie.reverts("ERROR:ADP-001:NOT_TEST_CHAIN"):
        usdc_feeder.forceDepegForNextPriceInfo({'from':productOwner})

    with brownie.reverts("Ownable: caller is not the owner"):
        usdc_feeder.forceDepegForNextPriceInfo({'from':instanceOperator})

    # check IPriceDataProvider.resetDepeg
    with brownie.reverts("ERROR:ADP-001:NOT_TEST_CHAIN"):
        usdc_feeder.resetDepeg({'from':productOwner})

    with brownie.reverts("Ownable: caller is not the owner"):
        usdc_feeder.resetDepeg({'from':instanceOperator})


def test_force_and_reset_depeg(
    usdc_feeder: UsdcPriceDataProvider, 
    instanceOperator:Account,
    productOwner:Account
):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    # create stable, valid, non-triggered, non-depegged initial state
    round_id = 36893488147419103822
    price = 100000017
    time = 1660297306
    # roundId qnswer startedAt updatedAt answeredInRound
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price, t=time)
    print('data1 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})

    round_id += 1
    price = 100000000
    time += 24 * 3600
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price, t=time)
    print('data2 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    price_info_depeg_init = usdc_feeder.getDepegPriceInfo().dict()
    print('price_info2 {}'.format(price_info))
    print('price_info_depeg_init {}'.format(price_info_depeg_init))

    assert price_info['id'] == round_id
    assert price_info['price'] == price
    assert price_info['compliance'] == STATE_COMPLIANCE['Valid']
    assert price_info['stability'] == STATE_STABILITY['Stable']
    assert price_info['triggeredAt'] == 0
    assert price_info['depeggedAt'] == 0
    assert price_info['createdAt'] == time

    assert price_info_depeg_init['id'] == 0
    assert price_info_depeg_init['price'] == 0
    assert price_info_depeg_init['compliance'] == STATE_COMPLIANCE['Undefined']
    assert price_info_depeg_init['stability'] == STATE_STABILITY['Undefined']
    assert price_info_depeg_init['triggeredAt'] == 0
    assert price_info_depeg_init['depeggedAt'] == 0
    assert price_info_depeg_init['createdAt'] == 0

    assert usdc_feeder.getTriggeredAt() == 0
    assert usdc_feeder.getDepeggedAt() == 0

    # move to triggered state
    round_id += 1
    price = 99500000
    time += 24 * 3600
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price, t=time)
    print('data3 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    print('price_info3 {}'.format(price_info))

    assert price_info['compliance'] == STATE_COMPLIANCE['FailedOnce']
    assert price_info['stability'] == STATE_STABILITY['Triggered']
    assert price_info['triggeredAt'] == time
    assert price_info['depeggedAt'] == 0

    assert usdc_feeder.getTriggeredAt() == time
    assert usdc_feeder.getDepeggedAt() == 0

    # check that non-owner cannot force depeg
    with brownie.reverts('Ownable: caller is not the owner'):
        usdc_feeder.forceDepegForNextPriceInfo({'from':instanceOperator})

    # prepare to move to depeg state
    tx = usdc_feeder.forceDepegForNextPriceInfo({'from':productOwner})
    print('tx.info() {}'.format(tx.info()))

    assert 'LogUsdcProviderForcedDepeg' in tx.events

    time_trigger = tx.events['LogUsdcProviderForcedDepeg']['updatedTriggeredAt']
    assert time - time_trigger == 24*3600
    assert usdc_feeder.getTriggeredAt() == time_trigger
    assert usdc_feeder.getDepeggedAt() == 0

    # move to depeg state
    round_id += 1
    price_depeg = 88700000
    time_depeg = time + 600
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price_depeg, t=time_depeg)
    print('data4 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    price_info_depeg = usdc_feeder.getDepegPriceInfo().dict()
    print('price_info4 {}'.format(price_info))
    print('price_info_depeg {}'.format(price_info_depeg))

    assert price_info['id'] == round_id
    assert price_info['price'] == price_depeg
    assert price_info['compliance'] == STATE_COMPLIANCE['FailedMultipleTimes']
    assert price_info['stability'] == STATE_STABILITY['Depegged']
    assert price_info['triggeredAt'] == time_trigger
    assert price_info['depeggedAt'] == time_depeg

    assert price_info['id'] == price_info_depeg['id']
    assert price_info['price'] == price_info_depeg['price']
    assert price_info['compliance'] == price_info_depeg['compliance']
    assert price_info['stability'] == price_info_depeg['stability']
    assert price_info['triggeredAt'] == price_info_depeg['triggeredAt']
    assert price_info['depeggedAt'] == price_info_depeg['depeggedAt']

    assert usdc_feeder.getTriggeredAt() == time_trigger
    assert usdc_feeder.getDepeggedAt() == time_depeg

    # add recovered price point
    round_id += 1
    price = 100000000
    time = time_depeg + 24 * 3600
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price, t=time)
    print('data5 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    price_info_depeg_new = usdc_feeder.getDepegPriceInfo().dict()

    # check price info
    assert price_info['id'] == round_id
    assert price_info['price'] == price
    assert price_info['compliance'] == STATE_COMPLIANCE['FailedMultipleTimes']
    assert price_info['stability'] == STATE_STABILITY['Depegged']
    assert price_info['triggeredAt'] == time_trigger
    assert price_info['depeggedAt'] == time_depeg
    assert price_info['createdAt'] == time

    # verify we're still depegged
    assert price_info_depeg_new['id'] == price_info_depeg['id']
    assert price_info_depeg_new['price'] == price_info_depeg['price']
    assert price_info_depeg_new['compliance'] == price_info_depeg['compliance']
    assert price_info_depeg_new['stability'] == price_info_depeg['stability']
    assert price_info_depeg_new['triggeredAt'] == price_info_depeg['triggeredAt']
    assert price_info_depeg_new['depeggedAt'] == price_info_depeg['depeggedAt']

    assert usdc_feeder.getTriggeredAt() == time_trigger
    assert usdc_feeder.getDepeggedAt() == time_depeg

    # check that non-owner cannot reset depeg
    with brownie.reverts('Ownable: caller is not the owner'):
        usdc_feeder.resetDepeg({'from':instanceOperator})

    # reset depeg state
    tx = usdc_feeder.resetDepeg({'from':productOwner})
    print('tx.info() {}'.format(tx.info()))

    assert 'LogUsdcProviderResetDepeg' in tx.events
    assert tx.events['LogUsdcProviderResetDepeg']['resetDepegAt'] > price_info_depeg['depeggedAt']

    assert usdc_feeder.getTriggeredAt() == 0
    assert usdc_feeder.getDepeggedAt() == 0

    # check effect on latest price info
    price_info = usdc_feeder.getLatestPriceInfo().dict()
    assert price_info['id'] == round_id
    assert price_info['price'] == price
    assert price_info['compliance'] == STATE_COMPLIANCE['FailedMultipleTimes']
    assert price_info['stability'] == STATE_STABILITY['Stable']
    assert price_info['triggeredAt'] == 0
    assert price_info['depeggedAt'] == 0
    assert price_info['createdAt'] == time

    # check effect on depeg price info
    price_info_depeg_reset = usdc_feeder.getDepegPriceInfo().dict()
    assert price_info_depeg_reset['id'] == 0
    assert price_info_depeg_reset['price'] == 0
    assert price_info_depeg_reset['compliance'] == STATE_COMPLIANCE['Undefined']
    assert price_info_depeg_reset['stability'] == STATE_STABILITY['Undefined']
    assert price_info_depeg_reset['triggeredAt'] == 0
    assert price_info_depeg_reset['depeggedAt'] == 0
    assert price_info_depeg_reset['createdAt'] == 0

    # return to valid compliance
    round_id += 1
    price = 100000001
    time = time_depeg + 24 * 3600
    data = '{id} {p} {t} {t} {id}'.format(id=round_id, p=price, t=time)
    print('data6 {}'.format(data))

    inject_data(usdc_feeder, data)
    usdc_feeder.processLatestPriceInfo({'from':instanceOperator})

    price_info = usdc_feeder.getLatestPriceInfo().dict()
    assert price_info['id'] == round_id
    assert price_info['price'] == price
    assert price_info['compliance'] == STATE_COMPLIANCE['Valid']
    assert price_info['stability'] == STATE_STABILITY['Stable']
    assert price_info['triggeredAt'] == 0
    assert price_info['depeggedAt'] == 0
    assert price_info['createdAt'] == time


def test_test_data(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for data in USDC_CHAINLINK_DATA:
        inject_data(usdc_feeder, data)

    for data in USDC_CHAINLINK_DATA:
        expected_data = data_to_round_data(data)
        round_id = expected_data[0]
        actual_data = usdc_feeder.getRoundData(round_id)
        check_round(actual_data, expected_data)

    if web3.chain_id == GANACHE:
        expected_data = data_to_round_data(USDC_CHAINLINK_DATA[-1])
        actual_data = usdc_feeder.latestRoundData()
        check_round(actual_data, expected_data)


def test_price_price_id_sequence_repeat(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_PRICE_SEQUENCE_REPEAT):
        inject_data(usdc_feeder, data)

        print('data[{}] {}'.format(i, data))

        # roundid 36893488147419103822
        if i in [0, 1]:
            # tx = usdc_feeder.getPriceInfo(price_id)
            tx = usdc_feeder.processLatestPriceInfo()
            price_info = tx.return_value.dict()
            print('price_info[{}] {}'.format(i, price_info))


def test_price_price_id_sequence_skip_one(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_PRICE_SEQUENCE_SKIP):
        inject_data(usdc_feeder, data)

        print('data[{}] {}'.format(i, data))

        # roundid 36893488147419103822
        if i in [0, 1]:
            # tx = usdc_feeder.getPriceInfo(price_id)
            tx = usdc_feeder.processLatestPriceInfo()
            price_info = tx.return_value.dict()
            print('price_info[{}] {}'.format(i, price_info))


def test_price_data_valid(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA):
        inject_data(usdc_feeder, data)

        price_id = data_to_round_data(data)[0]
        # tx = usdc_feeder.getPriceInfo(price_id)
        tx = usdc_feeder.processLatestPriceInfo()
        price_info = tx.return_value.dict()
        print('price_info[{}] {}'.format(i, price_info))

        if i == 0:
            assert price_info['compliance'] == STATE_COMPLIANCE['Initializing']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        else:
            assert price_info['compliance'] == STATE_COMPLIANCE['Valid']
            assert price_info['stability'] == STATE_STABILITY['Stable']


def test_price_data_heatbeat_error(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_HEARTBEAT_VIOLATED):
        inject_data(usdc_feeder, data)
        tx = usdc_feeder.processLatestPriceInfo()

        print('LogPriceDataHeartbeatExceeded in tx.events {} events {}'.format(
            'LogPriceDataHeartbeatExceeded' in tx.events,
            tx.events
        ))

        price_info = tx.return_value.dict()
        print('price_info[{}] {}'.format(i, price_info))

        (round_id, price, updated_at) = (price_info['id'], price_info['price'], price_info['createdAt'])
        compliance = usdc_feeder.getCompliance(round_id, price, updated_at).dict()

        if i == 0:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['Initializing']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 1:
            assert compliance['heartbeetIsValid'] is False
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['FailedOnce']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 2:
            assert compliance['heartbeetIsValid'] is False
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['FailedMultipleTimes']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 3:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['Valid']
            assert price_info['stability'] == STATE_STABILITY['Stable']


def test_price_data_deviation_error(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_DEVIATION_VIOLATED):
        inject_data(usdc_feeder, data)
        tx = usdc_feeder.processLatestPriceInfo()

        print('LogPriceDataDeviationExceeded in tx.events {} events {}'.format(
            'LogPriceDataDeviationExceeded' in tx.events,
            tx.events
        ))

        price_info = tx.return_value.dict()
        print('price_info[{}] {}'.format(i, price_info))

        (round_id, price, updated_at) = (price_info['id'], price_info['price'], price_info['createdAt'])
        compliance = usdc_feeder.getCompliance(round_id, price, updated_at).dict()

        if i == 0:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['Initializing']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 1:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is False
            assert price_info['compliance'] == STATE_COMPLIANCE['FailedOnce']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 2:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is False
            assert price_info['compliance'] == STATE_COMPLIANCE['FailedMultipleTimes']
            assert price_info['stability'] == STATE_STABILITY['Stable']
        elif i == 3:
            assert compliance['heartbeetIsValid'] is True
            assert compliance['priceDeviationIsValid'] is True
            assert price_info['compliance'] == STATE_COMPLIANCE['Valid']
            assert price_info['stability'] == STATE_STABILITY['Stable']


def test_price_data_trigger_and_recovery(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_TRIGGER_AND_RECOVER):
        inject_data(usdc_feeder, data)
        tx = usdc_feeder.processLatestPriceInfo()
        price_info = tx.return_value.dict()

        print('events[{}] {}'.format(
            i,
            tx.events
        ))

        # i createdAt  answer    comment
        # 0 1660070000 100000017 normal
        if i == 0:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Stable']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 1 1660080000  99700000 below recovery but above trigger
        elif i == 1:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Stable']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 2 1660090000  99500001 1 above trigger
        elif i == 2:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

            assert price_info['stability'] == STATE_STABILITY['Stable']
            assert price_info['triggeredAt'] == 0
            assert price_info['depeggedAt'] == 0
        # 3 1660100000  99500000 at trigger
        elif i == 3:
            triggeredAt = price_info['createdAt']
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0

            assert 'LogPriceDataProcessed' not in tx.events
            assert 'LogPriceDataTriggered' in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

            assert tx.events['LogPriceDataTriggered']['priceId'] == price_info['id']
            assert tx.events['LogPriceDataTriggered']['price'] == price_info['price']
            assert tx.events['LogPriceDataTriggered']['triggeredAt'] == price_info['triggeredAt']
            assert price_info['stability'] == STATE_STABILITY['Triggered']
            assert price_info['triggeredAt'] == triggeredAt
            assert price_info['depeggedAt'] == 0
        # 4 1660120000  99800000 above trigger but below recovery
        elif i == 4:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 5 1660140000  98000000 really below trigger
        elif i == 5:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 6 1660160000  99899999 1 below recovery
        elif i == 6:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 7 1660186401  99900000 at recovery
        elif i == 7:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0

            assert 'LogPriceDataProcessed' not in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

            assert tx.events['LogPriceDataRecovered']['priceId'] == price_info['id']
            assert tx.events['LogPriceDataRecovered']['price'] == price_info['price']
            assert tx.events['LogPriceDataRecovered']['triggeredAt'] == triggeredAt
            assert tx.events['LogPriceDataRecovered']['recoveredAt'] == price_info['createdAt']
            assert price_info['stability'] == STATE_STABILITY['Stable']
            assert price_info['triggeredAt'] == triggeredAt
            assert price_info['depeggedAt'] == 0
        # 8 1660200000  99700000 below recovery and above trigger
        elif i == 8:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

            assert price_info['stability'] == STATE_STABILITY['Stable']
            assert price_info['triggeredAt'] == 0
            assert price_info['depeggedAt'] == 0


def test_price_data_trigger_and_depeg(usdc_feeder: UsdcPriceDataProvider):

    if web3.chain_id != GANACHE:
        print('unsupported test case for chain_id {}'.format(web3.chain_id))
        return

    for i, data in enumerate(USDC_CHAINLINK_DATA_TRIGGER_AND_DEPEG):
        inject_data(usdc_feeder, data)

        event = usdc_feeder.isNewPriceInfoEventAvailable().dict()
        info = event['priceInfo'].dict()

        if i < 3:
            assert info['triggeredAt'] == 0
            assert info['triggeredAt'] == usdc_feeder.getTriggeredAt()
            assert info['depeggedAt'] == 0
            assert info['depeggedAt'] == usdc_feeder.getDepeggedAt()
        elif i > 3 and i < 7:
            assert info['triggeredAt'] > 0
            assert info['triggeredAt'] == usdc_feeder.getTriggeredAt()
            assert info['depeggedAt'] == 0
        elif i > 7:
            assert info['triggeredAt'] > 0
            assert info['triggeredAt'] == usdc_feeder.getTriggeredAt()
            assert info['depeggedAt'] > 0
            assert info['depeggedAt'] == usdc_feeder.getDepeggedAt()

        if i in [0, 1, 2, 4, 5, 6, 8, 9]:
            assert event['newEvent'] is False
            assert info['eventType'] == EVENT_TYPE['Update']            
        elif i == 3:
            assert event['newEvent'] is True
            assert info['eventType'] == EVENT_TYPE['TriggerEvent']
            assert info['triggeredAt'] == info['createdAt']
            assert info['depeggedAt'] == 0
        elif i == 7:
            assert event['newEvent'] is True
            assert info['eventType'] == EVENT_TYPE['DepegEvent']
            assert info['triggeredAt'] < info['depeggedAt']
            assert info['depeggedAt'] == info['createdAt']

        tx = usdc_feeder.processLatestPriceInfo()
        price_info = tx.return_value.dict()

        print('events[{}] {}'.format(
            i,
            tx.events
        ))

        # i createdAt  answer    comment
        # 0 1660070000 100000017 normal
        if i == 0:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Stable']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 1 1660080000  99700000 below recovery but above trigger
        elif i == 1:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Stable']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 2 1660090000  99500001 1 above trigger
        elif i == 2:
            assert usdc_feeder.getTriggeredAt() == 0
            assert usdc_feeder.getDepeggedAt() == 0
            assert len(tx.events) == 1
            assert 'LogPriceDataProcessed' in tx.events
            assert price_info['triggeredAt'] == 0
            assert price_info['depeggedAt'] == 0
            assert price_info['stability'] == STATE_STABILITY['Stable']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 3 1660100000  99500000 at trigger
        elif i == 3:
            triggeredAt = price_info['createdAt']
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0

            assert 'LogPriceDataProcessed' not in tx.events
            assert 'LogPriceDataTriggered' in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

            assert tx.events['LogPriceDataTriggered']['priceId'] == price_info['id']
            assert tx.events['LogPriceDataTriggered']['price'] == price_info['price']
            assert tx.events['LogPriceDataTriggered']['triggeredAt'] == price_info['triggeredAt']
            assert price_info['triggeredAt'] == triggeredAt
            assert price_info['depeggedAt'] == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']
        # 4 1660120000  99800000 above trigger but below recovery
        elif i == 4:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 5 1660140000  98000000 really below trigger
        elif i == 5:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 6 1660160000  99899999 1 below recovery
        elif i == 6:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == 0
            assert price_info['stability'] == STATE_STABILITY['Triggered']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events

        # 7 1660186401  99900000 at recovery, but too late -> depeg
        elif i == 7:
            depeggedAt = price_info['createdAt']
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == depeggedAt
            assert depeggedAt - triggeredAt == 24 * 3600 + 1

            assert 'LogPriceDataProcessed' not in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' in tx.events

            assert tx.events['LogPriceDataDepegged']['priceId'] == price_info['id']
            assert tx.events['LogPriceDataDepegged']['price'] == price_info['price']
            assert tx.events['LogPriceDataDepegged']['triggeredAt'] == triggeredAt
            assert tx.events['LogPriceDataDepegged']['depeggedAt'] == depeggedAt
            assert price_info['triggeredAt'] == triggeredAt
            assert price_info['depeggedAt'] == depeggedAt
            assert price_info['stability'] == STATE_STABILITY['Depegged']
        # 8 1660200000  99700000 below recovery and above trigger
        # still depegged because once depegged state remains at depegged no matter waht
        elif i in [8, 9]:
            assert usdc_feeder.getTriggeredAt() == triggeredAt
            assert usdc_feeder.getDepeggedAt() == depeggedAt
            assert price_info['triggeredAt'] == triggeredAt
            assert price_info['depeggedAt'] == depeggedAt
            assert price_info['stability'] == STATE_STABILITY['Depegged']

            assert 'LogPriceDataProcessed' in tx.events
            assert 'LogPriceDataTriggered' not in tx.events
            assert 'LogPriceDataRecovered' not in tx.events
            assert 'LogPriceDataDepegged' not in tx.events


def check_round(actual_data, expected_data):
    (
        round_id,
        answer,
        started_at,
        updated_at,
        answered_in_round
    ) = actual_data

    (
        expected_round_id,
        expected_answer,
        expected_started_at,
        expected_updated_at,
        expected_answered_in_round
    ) = expected_data

    assert round_id == expected_round_id
    assert answer == expected_answer
    assert started_at == expected_started_at
    assert updated_at == expected_updated_at
    assert answered_in_round == expected_answered_in_round


def inject_data(usdc_feeder, data):
    (
        round_id,
        answer,
        started_at,
        updated_at,
        answered_in_round
    ) = data_to_round_data(data)

    usdc_feeder.setRoundData(
        round_id,
        answer,
        started_at,
        updated_at,
        answered_in_round
    )


def data_to_round_data(data):
    round_data = data.split()
    round_id = int(round_data[0])
    answer = int(round_data[1])
    started_at = int(round_data[2])
    updated_at = int(round_data[3])
    answered_in_round = int(round_data[4])

    return (
        round_id,
        answer,
        started_at,
        updated_at,
        answered_in_round
    )
