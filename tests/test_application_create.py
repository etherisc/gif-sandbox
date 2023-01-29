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

from scripts.product import (
    GifProduct,
    GifRiskpool,
)

from scripts.deploy_product import to_token_amount
from scripts.deploy_fire import (
    create_bundle,
    create_policy
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
    token_address = instanceService.getComponentToken(riskpool.getId())
    token = interface.IERC20Metadata(token_address)

    # amount to stake in riskpool/bundle
    bundle_funding = 10 ** 6
    bundle_funding_amount = to_token_amount(token, bundle_funding)

    # check initialized riskpool
    assert instanceService.bundles() == 0
    assert token.balanceOf(instanceWallet) == 0
    assert token.balanceOf(riskpoolWallet) == 0
    assert token.balanceOf(investor) == 0
    assert token.balanceOf(instanceOperator) >= bundle_funding_amount

    # create riskpool / bundle setup
    bundle_id = create_bundle(
        instance, 
        instanceOperator, 
        riskpool, 
        investor, 
        bundle_funding=bundle_funding)

    riskpoolBalanceBefore = instanceService.getBalance(riskpool.getId())
    instanceBalanceBefore = token.balanceOf(instanceWallet)

    # create policy
    object_name = "My House"
    object_value = 10 ** 5
    sum_insured_amount = to_token_amount(token, object_value)

    process_id = create_policy(
        instance, 
        instanceOperator, 
        product, 
        customer, 
        object_name=object_name,
        object_value=object_value)

    tx = history[-1]
    assert 'LogFirePolicyCreated' in tx.events
    assert tx.events['LogFirePolicyCreated']['processId'] == process_id
    assert tx.events['LogFirePolicyCreated']['policyHolder'] == customer
    assert tx.events['LogFirePolicyCreated']['sumInsured'] == sum_insured_amount
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
    assert application['sumInsuredAmount'] == sum_insured_amount
    premium = application['premiumAmount']

    riskpoolBalanceAfter = instanceService.getBalance(riskpool.getId())
    instanceBalanceAfter = token.balanceOf(instanceWallet)

    # check policy
    assert policy['premiumExpectedAmount'] == premium
    assert policy['premiumPaidAmount'] == premium
    assert policy['claimsCount'] == 0
    assert policy['openClaimsCount'] == 0
    assert policy['payoutMaxAmount'] == sum_insured_amount
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
    token_address = instanceService.getComponentToken(riskpool.getId())
    token = interface.IERC20Metadata(token_address)
    bundle_funding = 10 ** 6
    bundle_funding_amount = to_token_amount(token, bundle_funding)

    # create riskpool / bundle setup
    bundle_id = create_bundle(
        instance, 
        instanceOperator, 
        riskpool, 
        investor, 
        bundle_funding=bundle_funding)

    riskpool.lockBundle(bundle_id, {'from':investor})

    object_name = "My House"
    object_value = 10 ** 5
    sum_insured_amount = to_token_amount(token, object_value)

    with brownie.reverts('ERROR:BRP-001:NO_ACTIVE_BUNDLES'):
        create_policy(
            instance, 
            instanceOperator, 
            product, 
            customer, 
            object_name=object_name,
            object_value=object_value)
