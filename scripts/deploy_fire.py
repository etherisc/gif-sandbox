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

from scripts.deploy_product import (
    all_in_1_base,
    verify_deploy_base,
    from_component_base,
    from_registry_base,
    stakeholders_accounts_ganache,
    fund_and_create_allowance,
    get_product_token,
    get_riskpool_token,
    get_bundle_id,
    get_process_id,
    to_token_amount
)

# product/oracle/riskpool base name
BASE_NAME = 'Fire'

# default setup for all_in_1 -> creatd_policy
OBJECT_NAME = 'My Home'
OBJECT_VALUE = 10 ** 5

# default setup for all_in_1 -> create_bundle
BUNDLE_FUNDING = 10 ** 6

# contract classes for all_in_1
CONTRACT_CLASS_TOKEN = Usdc
CONTRACT_CLASS_PRODUCT = FireProduct
CONTRACT_CLASS_ORACLE = FireOracle
CONTRACT_CLASS_RISKPOOL = FireRiskpool


def help():
    print('from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help')
    print('(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instance, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=True)')
    print('verify_deploy(d, usdc, product)')
    print('instanceService.getBundle(bundleId).dict()')
    print('instanceService.getPolicy(processId).dict()')


def create_bundle(
    instance, 
    instance_operator,
    riskpool,
    investor,
    bundle_funding = BUNDLE_FUNDING
):
    # fund riskpool with risk bundle
    token = get_riskpool_token(riskpool)
    funding_amount = to_token_amount(token, bundle_funding)

    fund_and_create_allowance(
        instance,
        instance_operator,
        investor,
        token,
        funding_amount)

    # create new risk bundle
    bundle_filter = ""
    tx = riskpool.createBundle(
        bundle_filter,
        funding_amount, 
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
    sum_insured_amount = to_token_amount(token, object_value)
    premium_amount = product.calculatePremium(sum_insured_amount)

    fund_and_create_allowance(
        instance,
        instance_operator,
        customer,
        token,
        premium_amount)
    
    # create new policy
    tx = product.applyForPolicy(
        object_name,
        sum_insured_amount,
        {'from': customer})

    return get_process_id(tx)


def all_in_1(
    stakeholders_accounts=None,
    registry_address=None,
    usdc_address=None,
    deploy_all=False,
    publish_source=False
):
    return all_in_1_base(
        BASE_NAME,
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
    verify_deploy_base(
        from_component,
        stakeholder_accounts, 
        token, 
        product)


def from_component(
    component_address,
    product_id=0,
    oracle_id=0,
    riskpool_id=0
):
    return from_component_base(
        component_address,
        CONTRACT_CLASS_PRODUCT,
        CONTRACT_CLASS_ORACLE,
        CONTRACT_CLASS_RISKPOOL,
        product_id, 
        oracle_id, 
        riskpool_id)


def from_registry(
    registry_address,
    product_id=0,
    oracle_id=0,
    riskpool_id=0
):
    return from_registry_base(
        registry_address,
        CONTRACT_CLASS_PRODUCT,
        CONTRACT_CLASS_ORACLE,
        CONTRACT_CLASS_RISKPOOL,
        product_id, 
        oracle_id, 
        riskpool_id)
