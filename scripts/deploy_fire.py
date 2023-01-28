from brownie.network import accounts
from brownie.network.account import Account
from brownie import (
    interface,
    network,
    web3,
    Usdc,
    FireProduct,
    FireOracle,
    FireRiskpool
)

from scripts.product import GifProductComplete
from scripts.instance import GifInstance
from scripts.deploy_product import (
    all_in_1_base,
    verify_deploy_base,
    fund_and_create_allowance,
    get_product_token,
    get_riskpool_token,
    get_bundle_id,
    get_process_id
)

# default setup for all_in_1 -> creatd_policy
OBJECT_NAME = 'My Home'
OBJECT_VALUE = 10 ** 5

# default setup for all_in_1 -> create_bundle
BUNDLE_FUNDING = 10 ** 6

# contract clases for all_in_1
CONTRACT_CLASS_TOKEN = Usdc
CONTRACT_CLASS_PRODUCT = FireProduct
CONTRACT_CLASS_ORACLE = FireOracle
CONTRACT_CLASS_RISKPOOL = FireRiskpool


def help():
    print('from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help')
    print('(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=True)')
    print('verify_deploy(d, usdc, product)')
    print('instanceService.getBundle(bundleId).dict()')
    print('instanceService.getPolicy(processId).dict()')


def all_in_1(
    stakeholders_accounts=None,
    registry_address=None,
    usdc_address=None,
    deploy_all=False,
    publish_source=False
):
    return all_in_1_base(
        CONTRACT_CLASS_TOKEN, 
        CONTRACT_CLASS_PRODUCT, 
        CONTRACT_CLASS_ORACLE, 
        CONTRACT_CLASS_RISKPOOL,
        create_bundle,
        create_policy,
        stakeholders_accounts,
        registry_address,
        usdc_address,
        deploy_all=deploy_all,
        publish_source=publish_source
    )


def verify_deploy(
    stakeholder_accounts, 
    token,
    product
):
    verify_deploy_base(stakeholder_accounts, token, product)


def create_bundle(
    instance, 
    instance_operator,
    riskpool,
    investor,
    bundle_funding = BUNDLE_FUNDING
):
    # fund riskpool with risk bundle
    token = get_riskpool_token(riskpool)
    funding = bundle_funding * 10 ** token.decimals()

    fund_and_create_allowance(
        instance,
        instance_operator,
        investor,
        token,
        funding)

    # create new risk bundle
    bundle_filter = ""
    tx = riskpool.createBundle(
        bundle_filter,
        funding, 
        {'from': investor})

    return get_bundle_id(tx)


def create_policy(
    instance, 
    instance_operator,
    product,
    customer,
    object_name = OBJECT_NAME,
    object_value = OBJECT_VALUE
):
    # fund customer to pay premium
    token = get_product_token(product)
    sum_insured = object_value * 10 ** token.decimals()
    premium = product.calculatePremium(sum_insured)

    fund_and_create_allowance(
        instance,
        instance_operator,
        customer,
        token,
        premium)
    
    # create new policy
    tx = product.applyForPolicy(
        object_name,
        sum_insured,
        {'from': customer})

    return get_process_id(tx)
