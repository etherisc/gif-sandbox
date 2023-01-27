import pytest

from brownie.network.account import Account

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_test_coin(
    instanceOperator: Account,
    testCoin,
):
    assert testCoin.symbol() == 'TDY'
    assert testCoin.balanceOf(instanceOperator) == 1000000000000000000000000
