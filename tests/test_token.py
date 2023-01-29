import pytest

from brownie.network.account import Account

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_token_fixture(
    instanceOperator: Account,
    token,
):
    assert token.name() == 'USD Coin - DUMMY'
    assert token.symbol() == 'USDC'
    assert token.decimals() == 6
    assert token.balanceOf(instanceOperator) == 1000000000000000000000000
