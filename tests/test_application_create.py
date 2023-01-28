import brownie
import pytest

from brownie.network.account import Account
from brownie import (
    chain,
    history,
    interface
)

from scripts.util import (
    b2s,
    contract_from_address
)

from scripts.product_fire import (
    GifFireProduct,
    GifFireRiskpool,
)

from scripts.setup import (
    create_bundle, 
    apply_for_policy,
)

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_create_application(
    instance,
    instanceService,
    instanceOperator,
    instanceWallet,
    investor,
    customer,
    product,
    riskpool
):
    instanceWallet = instanceService.getInstanceWallet()
    riskpoolWallet = instanceService.getRiskpoolWallet(riskpool.getId())
    tokenAddress = instanceService.getComponentToken(riskpool.getId())
    token = interface.IERC20(tokenAddress)

    bundle_id = create_bundle(
        instance, 
        instanceOperator, 
        investor, 
        riskpool)

    riskpoolBalanceBefore = instanceService.getBalance(riskpool.getId())
    instanceBalanceBefore = token.balanceOf(instanceWallet)

    object_name = "My House"
    sum_insured = 100000
    process_id = apply_for_policy(
        object_name,
        instance,
        instanceOperator,
        product,
        customer,
        sum_insured)

    tx = history[-1]
    assert 'LogFirePolicyCreated' in tx.events
    assert tx.events['LogFirePolicyCreated']['processId'] == process_id
    assert tx.events['LogFirePolicyCreated']['policyHolder'] == customer
    assert tx.events['LogFirePolicyCreated']['sumInsured'] == sum_insured
    assert tx.events['LogFirePolicyCreated']['objectName'] == object_name

    metadata = instanceService.getMetadata(process_id).dict()
    application = instanceService.getApplication(process_id).dict()
    policy = instanceService.getPolicy(process_id).dict()

    print('policy {} created'.format(process_id))
    print('metadata {}'.format(metadata))
    print('application {}'.format(application))
    print('policy {}'.format(policy))

    # check metadata
    assert metadata['owner'] == customer
    assert metadata['productId'] == product.getId()

    # check application
    assert application['sumInsuredAmount'] == sum_insured
    premium = application['premiumAmount']

    riskpoolBalanceAfter = instanceService.getBalance(riskpool.getId())
    instanceBalanceAfter = token.balanceOf(instanceWallet)

    # check policy
    assert policy['premiumExpectedAmount'] == premium
    assert policy['premiumPaidAmount'] == premium
    assert policy['claimsCount'] == 0
    assert policy['openClaimsCount'] == 0
    assert policy['payoutMaxAmount'] == sum_insured
    assert policy['payoutAmount'] == 0

    # check wallet balances
    assert riskpoolBalanceAfter < riskpoolBalanceBefore + premium
    assert riskpoolBalanceAfter > riskpoolBalanceBefore

    # check instance wallet balance
    fee = riskpoolBalanceBefore + premium - riskpoolBalanceAfter
    assert instanceBalanceAfter == instanceBalanceBefore + fee


def test_application_with_locked_bundle(
    instance,
    instanceService,
    instanceOperator,
    investor,
    customer,
    product,
    riskpool,
):
    bundle_id = create_bundle(
        instance, 
        instanceOperator, 
        investor, 
        riskpool)

    riskpool.lockBundle(bundle_id, {'from':investor})

    object_name = 'My 1st House'
    sum_insured = 100000

    with brownie.reverts('ERROR:BRP-001:NO_ACTIVE_BUNDLES'):
        apply_for_policy(
            object_name,
            instance,
            instanceOperator,
            product,
            customer,
            sum_insured)
