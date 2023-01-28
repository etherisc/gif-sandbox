from brownie.network import accounts
from brownie.network.account import Account

from brownie import (
    interface,
    network,
    web3,
    Usdc,
    CoorestProduct,
    CoorestOracle,
    CoorestRiskpool
)

from scripts.product import GifProductComplete
from scripts.instance import GifInstance
from scripts.util import s2b
from scripts.deploy_product import (
    all_in_1_base,
    verify_deploy_base,
    stakeholders_accounts_ganache,
    INSURER,
    fund_and_create_allowance,
    get_product_token,
    get_riskpool_token,
    get_bundle_id,
    get_process_id
)

# default setup for all_in_1 -> creatd_policy
PREMIUM = 500
SUM_INSURED = 10000
PROJECT_ID = 'Coorest Project'

# default setup for all_in_1 -> create_bundle
BUNDLE_FUNDING = 10 * SUM_INSURED

CONTRACT_CLASS_TOKEN = Usdc
CONTRACT_CLASS_PRODUCT = CoorestProduct
CONTRACT_CLASS_ORACLE = CoorestOracle
CONTRACT_CLASS_RISKPOOL = CoorestRiskpool


def help():
    print('from scripts.deploy_coorest import all_in_1, verify_deploy, create_bundle, create_policy, help')
    print('(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=True)')
    print('verify_deploy(d, usdc, product)')
    print('instanceService.getPolicy(processId).dict()')
    print('instanceService.getBundle(1).dict()')


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
    premium=PREMIUM,
    sum_insured=SUM_INSURED,
    project_id=PROJECT_ID,
):
    # fund customer to pay premium
    token = get_product_token(product)

    fund_and_create_allowance(
        instance,
        instance_operator,
        customer,
        token,
        premium)
    
    # ensure insurer has its role for product
    insurer = stakeholders_accounts_ganache()[INSURER]
    product.grantInsurerRole(insurer)

    # create risk
    risk_id = create_risk(product, insurer, project_id)
    
    # create new policy
    tx = product.applyForPolicy(
        customer,
        premium,
        sum_insured,
        risk_id,
        {'from': insurer})

    return get_process_id(tx)


def create_risk(
    product,
    insurer,
    project_id:str,
):
    project_id_bytes = s2b(project_id)
    tx = product.createRisk(project_id_bytes, {'from': insurer})
    return product.calculateRiskId(project_id_bytes)
