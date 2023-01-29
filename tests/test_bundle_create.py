import brownie
import pytest

from brownie.network.account import Account
from brownie import (
    interface,
)

from scripts.util import b2s

from scripts.product import (
    GifProduct,
    GifRiskpool,
)

from scripts.deploy_product import to_token_amount
from scripts.deploy_fire import create_bundle

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_create_bundle_happy_case(
    instance,
    instanceService,
    instanceOperator,
    investor,
    riskpool,
):
    instanceWallet = instanceService.getInstanceWallet()
    riskpoolWallet = instanceService.getRiskpoolWallet(riskpool.getId())
    tokenAddress = instanceService.getComponentToken(riskpool.getId())
    token = interface.IERC20Metadata(tokenAddress)

    bundle_funding = 100000
    bundle_funding_amount = to_token_amount(token, bundle_funding)

    # check initialized riskpool
    assert instanceService.bundles() == 0
    assert token.balanceOf(instanceWallet) == 0
    assert token.balanceOf(riskpoolWallet) == 0
    assert token.balanceOf(investor) == 0
    assert token.balanceOf(instanceOperator) >= bundle_funding

    bundleId = create_bundle(
        instance, 
        instanceOperator, 
        riskpool, 
        investor, 
        bundle_funding=bundle_funding)

    # check wallet balances against bundle investment
    fixedFee = 0
    fractionalFee = 0
    capital_fees = fractionalFee * bundle_funding_amount + fixedFee
    net_capital = bundle_funding_amount - capital_fees

    assert instanceService.bundles() == 1
    assert token.balanceOf(riskpoolWallet) == net_capital
    assert token.balanceOf(instanceWallet) == capital_fees

    print('bundle {} created'.format(bundleId))

    # check riskpool statistics
    assert instanceService.getCapital(riskpool.getId()) == net_capital
    assert instanceService.getCapacity(riskpool.getId()) == net_capital
    assert instanceService.getBalance(riskpool.getId()) == net_capital
    assert instanceService.getTotalValueLocked(riskpool.getId()) == 0

    # check bundle statistics
    (
        id, 
        riskpoolId, 
        tokenId, 
        state, 
        bundleFilter, 
        capital, 
        lockedCapital, 
        balance, 
        createdAt, 
        updatedAt
    ) = instanceService.getBundle(bundleId)

    assert id == bundleId
    assert riskpoolId == riskpool.getId()
    assert state == 0 # enum BundleState { Active, Locked, Closed, Burned }
    assert capital == net_capital
    assert lockedCapital == 0
    assert balance == net_capital
    assert createdAt > 0
    assert updatedAt == createdAt
