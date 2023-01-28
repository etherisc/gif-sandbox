from brownie.network.account import Account

# pylint: disable-msg=E0611
from brownie import (
    interface,
    FireProduct,
    FireRiskpool
)

from scripts.instance import GifInstance
from scripts.util import contract_from_address

USDC_DECIMALS = 6
USDC_MULTIPLIER = 10 ** USDC_DECIMALS
DEFAULT_BUNDLE_FUNDING = 10 ** 6 * USDC_MULTIPLIER
DEFAULT_SUM_INSURED = 10 ** 5 * USDC_MULTIPLIER

# a house for 100'000 will have a yearly premium of 2000
SUM_INSURED_FACTOR = 0.02

def fund_account(
    instance: GifInstance, 
    owner: Account,
    account: Account,
    token: interface.IERC20,
    amount: int
):
    token.transfer(account, amount, {'from': owner})
    token.approve(instance.getTreasury(), amount, {'from': account})


def create_bundle(
    instance: GifInstance, 
    instanceOperator: Account,
    investor: Account,
    riskpool: FireRiskpool,
    funding: int = DEFAULT_BUNDLE_FUNDING
) -> int:
    # get token from riskpool
    tokenAddress = riskpool.getErc20Token()
    token = contract_from_address(interface.IERC20, tokenAddress)

    # fund investor and create allowance for investment
    instanceService = instance.getInstanceService()
    token.transfer(investor, funding, {'from': instanceOperator})
    token.approve(instanceService.getTreasuryAddress(), funding, {'from': investor})

    # create bundle
    bundleFilter = ""
    tx = riskpool.createBundle(
        bundleFilter,
        funding, 
        {'from': investor})

    # return bundle id
    return tx.events['LogRiskpoolBundleCreated']['bundleId']


def apply_for_policy(
    object_name: str,
    instance: GifInstance, 
    instance_operator: Account,
    product: FireProduct, 
    customer: Account,
    sum_insured: int = DEFAULT_SUM_INSURED
):
    # get token from product
    token_address = product.getToken()
    token = contract_from_address(interface.IERC20, token_address)

    # calculate premium for sum insured
    premium = SUM_INSURED_FACTOR * sum_insured

    # transfer premium funds to customer and create allowance
    token.transfer(customer, premium, {'from': instance_operator})
    token.approve(instance.getTreasury(), premium, {'from': customer})

    # create policy
    tx = product.applyForPolicy(
        object_name,
        premium,
        sum_insured,
        {'from': customer})

    # return policy id (= process id)
    return tx.events['LogApplicationCreated']['processId']
