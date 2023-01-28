import pytest

from brownie.network.account import Account

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_usdc_fixture(
    instanceOperator: Account,
    usdc,
):
    assert usdc.name() == 'USD Coin - DUMMY'
    assert usdc.symbol() == 'USDC'
    assert usdc.decimals() == 6
    assert usdc.balanceOf(instanceOperator) == 1000000000000000000000000
