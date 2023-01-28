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

from scripts.product_fire import GifFireProductComplete
from scripts.instance import GifInstance

from scripts.setup import (
    create_bundle,
    apply_for_policy
)

from scripts.util import (
    contract_from_address,
    get_package
)

from os.path import exists

# product specific constants
OBJECT_NAME = 'My Home'

# instance specific constants
REGISTRY_OWNER = 'registryOwner'
INSTANCE_OPERATOR = 'instanceOperator'
INSTANCE_WALLET = 'instanceWallet'
ORACLE_PROVIDER = 'oracleProvider'
RISKPOOL_KEEPER = 'riskpoolKeeper'
RISKPOOL_WALLET = 'riskpoolWallet'
INVESTOR = 'investor'
PRODUCT_OWNER = 'productOwner'
CUSTOMER1 = 'customer1'
CUSTOMER2 = 'customer2'

ERC20_TOKEN = 'erc20Token'
INSTANCE = 'instance'
INSTANCE_SERVICE = 'instanceService'
INSTANCE_OPERATOR_SERVICE = 'instanceOperatorService'
COMPONENT_OWNER_SERVICE = 'componentOwnerService'
PRODUCT = 'product'
ORACLE = 'oracle'
RISKPOOL = 'riskpool'

PROCESS_ID1 = 'processId1'
PROCESS_ID2 = 'processId2'

# GAS_PRICE = web3.eth.gas_price
GAS_PRICE = 25000000
GAS_PRICE_SAFETY_FACTOR = 1.25

GAS_S = 2000000
GAS_M = 3 * GAS_S
GAS_L = 10 * GAS_M

REQUIRED_FUNDS_S = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_S)
REQUIRED_FUNDS_M = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_M)
REQUIRED_FUNDS_L = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_L)

INITIAL_ERC20_BUNDLE_FUNDING = 100000

REQUIRED_FUNDS = {
    INSTANCE_OPERATOR: REQUIRED_FUNDS_L,
    INSTANCE_WALLET:   REQUIRED_FUNDS_S,
    PRODUCT_OWNER:     REQUIRED_FUNDS_M,
    RISKPOOL_KEEPER:   REQUIRED_FUNDS_M,
    RISKPOOL_WALLET:   REQUIRED_FUNDS_S,
    INVESTOR:          REQUIRED_FUNDS_S,
    CUSTOMER1:         REQUIRED_FUNDS_S,
    CUSTOMER2:         REQUIRED_FUNDS_S,
}


def help():
    print('from scripts.deploy_fire import all_in_1, verify_deploy, new_bundle, new_policy, inspect_bundles, inspect_applications, help')
    print('(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instanceService, instanceOperator, processId, d) = all_in_1(deploy_all=True)')
    print('verify_deploy(d, usdc, product)')
    print('instanceService.getPolicy(processId).dict()')
    print('instanceService.getBundle(1).dict()')
    print('inspect_bundles(d)')
    print('inspect_applications(d)')


def verify_deploy(
    stakeholder_accounts, 
    erc20_token,
    product
):
    # define stakeholder accounts
    a = stakeholder_accounts
    instanceOperator=a[INSTANCE_OPERATOR]
    instanceWallet=a[INSTANCE_WALLET]
    riskpoolKeeper=a[RISKPOOL_KEEPER]
    riskpoolWallet=a[RISKPOOL_WALLET]
    oracleProvider=a[ORACLE_PROVIDER]
    productOwner=a[PRODUCT_OWNER]
    investor=a[INVESTOR]
    customer=a[CUSTOMER1]

    registry_address = product.getRegistry()
    product_id = product.getId()
    oracle_id = product.getOracleId()
    riskpool_id = product.getRiskpoolId()

    (
        instance,
        product,
        oracle,
        riskpool
    ) = from_component(
        product.address, 
        productId=product_id,
        oracleId=oracle_id,
        riskpoolId=riskpool_id
    )

    instanceService = instance.getInstanceService()
    verify_element('Registry', instanceService.getRegistry(), registry_address)
    verify_element('InstanceOperator', instanceService.getInstanceOperator(), instanceOperator)
    verify_element('InstanceWallet', instanceService.getInstanceWallet(), instanceWallet)

    verify_element('RiskpoolId', riskpool.getId(), riskpool_id)
    verify_element('RiskpoolType', instanceService.getComponentType(riskpool_id), 2)
    verify_element('RiskpoolState', instanceService.getComponentState(riskpool_id), 3)
    verify_element('RiskpoolContract', riskpool.address, instanceService.getComponent(riskpool_id))
    verify_element('RiskpoolKeeper', riskpool.owner(), riskpoolKeeper)
    verify_element('RiskpoolWallet', instanceService.getRiskpoolWallet(riskpool_id), riskpoolWallet)
    verify_element('RiskpoolBalance', instanceService.getBalance(riskpool_id), erc20_token.balanceOf(riskpoolWallet))
    verify_element('RiskpoolToken', riskpool.getErc20Token(), erc20_token.address)

    verify_element('ProductId', product.getId(), product_id)
    verify_element('ProductType', instanceService.getComponentType(product_id), 1)
    verify_element('ProductState', instanceService.getComponentState(product_id), 3)
    verify_element('ProductDepegState', product.getDepegState(), 1) # active
    verify_element('ProductContract', product.address, instanceService.getComponent(product_id))
    verify_element('ProductOwner', product.owner(), productOwner)
    verify_element('ProductProtectedToken', product.getProtectedToken(), erc20_protected_token.address)
    verify_element('ProductToken', product.getToken(), erc20_token.address)
    verify_element('ProductRiskpool', product.getRiskpoolId(), riskpool_id)

    print('InstanceWalletBalance {:.2f}'.format(erc20_token.balanceOf(instanceService.getInstanceWallet())/10**erc20_token.decimals()))
    print('RiskpoolWalletTVL {:.2f}'.format(instanceService.getTotalValueLocked(riskpool_id)/10**erc20_token.decimals()))
    print('RiskpoolWalletCapacity {:.2f}'.format(instanceService.getCapacity(riskpool_id)/10**erc20_token.decimals()))
    print('RiskpoolWalletBalance {:.2f}'.format(erc20_token.balanceOf(instanceService.getRiskpoolWallet(riskpool_id))/10**erc20_token.decimals()))

    print('RiskpoolBundles {}'.format(riskpool.bundles()))
    print('ProductApplications {}'.format(product.applications()))

    print('--- inspect_bundles(d) ---')
    inspect_bundles(stakeholder_accounts)
    print('--- inspect_applications(d) ---')
    inspect_applications(stakeholder_accounts)


def verify_element(
    element,
    value,
    expected_value
):
    if value == expected_value:
        print('{} OK {}'.format(element, value))
    else:
        print('{} ERROR {} expected {}'.format(element, value, expected_value))


def stakeholders_accounts_ganache():
    # define stakeholder accounts  
    instanceOperator=accounts[0]
    instanceWallet=accounts[1]
    riskpoolKeeper=accounts[2]
    riskpoolWallet=accounts[3]
    investor=accounts[4]
    oracleProvider=accounts[5]
    productOwner=accounts[6]
    customer=accounts[7]
    customer2=accounts[8]

    return {
        INSTANCE_OPERATOR: instanceOperator,
        INSTANCE_WALLET: instanceWallet,
        RISKPOOL_KEEPER: riskpoolKeeper,
        RISKPOOL_WALLET: riskpoolWallet,
        INVESTOR: investor,
        ORACLE_PROVIDER: oracleProvider,
        PRODUCT_OWNER: productOwner,
        CUSTOMER1: customer,
        CUSTOMER2: customer2,
    }


def check_funds(stakeholders_accounts, erc20_token):
    _print_constants()

    a = stakeholders_accounts

    native_token_success = True
    fundsMissing = 0
    for accountName, requiredAmount in REQUIRED_FUNDS.items():
        if a[accountName].balance() >= REQUIRED_FUNDS[accountName]:
            print('{} funding ok'.format(accountName))
        else:
            fundsMissing += REQUIRED_FUNDS[accountName] - a[accountName].balance()
            print('{} needs {} but has {}'.format(
                accountName,
                REQUIRED_FUNDS[accountName],
                a[accountName].balance()
            ))
    
    if fundsMissing > 0:
        native_token_success = False

        if a[INSTANCE_OPERATOR].balance() >= REQUIRED_FUNDS[INSTANCE_OPERATOR] + fundsMissing:
            print('{} sufficiently funded with native token to cover missing funds'.format(INSTANCE_OPERATOR))
        else:
            additionalFunds = REQUIRED_FUNDS[INSTANCE_OPERATOR] + fundsMissing - a[INSTANCE_OPERATOR].balance()
            print('{} needs additional funding of {} ({} ETH) with native token to cover missing funds'.format(
                INSTANCE_OPERATOR,
                additionalFunds,
                additionalFunds/10**18
            ))
    else:
        native_token_success = True

    erc20_success = False
    if erc20_token:
        erc20_success = check_erc20_funds(a, erc20_token)
    else:
        print('WARNING: no erc20 token defined, skipping erc20 funds checking')

    return native_token_success & erc20_success


def check_erc20_funds(a, erc20_token):
    if erc20_token.balanceOf(a[INSTANCE_OPERATOR]) >= INITIAL_ERC20_BUNDLE_FUNDING:
        print('{} ERC20 funding ok'.format(INSTANCE_OPERATOR))
        return True
    else:
        print('{} needs additional ERC20 funding of {} to cover missing funds'.format(
            INSTANCE_OPERATOR,
            INITIAL_ERC20_BUNDLE_FUNDING - erc20_token.balanceOf(a[INSTANCE_OPERATOR])))
        print('IMPORTANT: manual transfer needed to ensure ERC20 funding')
        return False


def amend_funds(stakeholders_accounts):
    a = stakeholders_accounts
    for accountName, requiredAmount in REQUIRED_FUNDS.items():
        if a[accountName].balance() < REQUIRED_FUNDS[accountName]:
            missingAmount = REQUIRED_FUNDS[accountName] - a[accountName].balance()
            print('funding {} with {}'.format(accountName, missingAmount))
            a[INSTANCE_OPERATOR].transfer(a[accountName], missingAmount)

    print('re-run check_funds() to verify funding before deploy')


def _print_constants():
    print('chain id: {}'.format(web3.eth.chain_id))
    print('gas price [Mwei]: {}'.format(GAS_PRICE/10**6))
    print('gas price safety factor: {}'.format(GAS_PRICE_SAFETY_FACTOR))

    print('gas S: {}'.format(GAS_S))
    print('gas M: {}'.format(GAS_M))
    print('gas L: {}'.format(GAS_L))

    print('required S [ETH]: {}'.format(REQUIRED_FUNDS_S / 10**18))
    print('required M [ETH]: {}'.format(REQUIRED_FUNDS_M / 10**18))
    print('required L [ETH]: {}'.format(REQUIRED_FUNDS_L / 10**18))


def _get_balances(stakeholders_accounts):
    balance = {}

    for account_name, account in stakeholders_accounts.items():
        balance[account_name] = account.balance()

    return balance


def _get_balances_delta(balances_before, balances_after):
    balance_delta = { 'total': 0 }

    for accountName, account in balances_before.items():
        balance_delta[accountName] = balances_before[accountName] - balances_after[accountName]
        balance_delta['total'] += balance_delta[accountName]
    
    return balance_delta


def _pretty_print_delta(title, balances_delta):

    print('--- {} ---'.format(title))
    
    gasPrice = network.gas_price()
    print('gas price: {}'.format(gasPrice))

    for accountName, amount in balances_delta.items():
        if accountName != 'total':
            if gasPrice != 'auto':
                print('account {}: gas {}'.format(accountName, amount / gasPrice))
            else:
                print('account {}: amount {}'.format(accountName, amount))
    
    print('-----------------------------')
    if gasPrice != 'auto':
        print('account total: gas {}'.format(balances_delta['total'] / gasPrice))
    else:
        print('account total: amount {}'.format(balances_delta['total']))
    print('=============================')


def instance_from_registry_X(
    stakeholders_accounts,
    registry_address,
):
    instance = GifInstance(
        stakeholders_accounts[INSTANCE_OPERATOR], 
        instanceWallet=instanceWallet)

    deployment = _add_instance_to_deployment(
        stakeholders_accounts,
        instance)

    return deployment


def deploy_new_instance_X(
    stakeholders_accounts,
    dip_token,
    erc20_protected_token,
    erc20_token,
    publish_source=False
):
    # define stakeholder accounts
    a = stakeholders_accounts
    instanceOperator=a[INSTANCE_OPERATOR]
    instanceWallet=a[INSTANCE_WALLET]
    riskpoolKeeper=a[RISKPOOL_KEEPER]
    riskpoolWallet=a[RISKPOOL_WALLET]
    investor=a[INVESTOR]
    productOwner=a[PRODUCT_OWNER]
    customer=a[CUSTOMER1]
    customer2=a[CUSTOMER2]
    staker=a[STAKER]

    mult_dip = 10**dip_token.decimals()
    mult = 10**erc20_token.decimals()

    if not check_funds(a, erc20_token):
        print('ERROR: insufficient funding, aborting deploy')
        return

    # # assess balances at beginning of deploy
    # balances_before = _get_balances(stakeholders_accounts)

    # if not dip_token:
    #     print('ERROR: no dip token defined, aborting deploy')
    #     return

    # if not erc20_protected_token:
    #     print('ERROR: no protected erc20 defined, aborting deploy')
    #     return

    # if not erc20_token:
    #     print('ERROR: no erc20 defined, aborting deploy')
    #     return

    # print('====== token setup ======')
    # print('- dip {} {}'.format(dip_token, dip_token.symbol()))
    # print('- protected {} {}'.format(erc20_protected_token, erc20_protected_token.symbol()))
    # print('- premium {} {}'.format(erc20_token, erc20_token.symbol()))
    
    erc20Token = erc20_token

    print('====== deploy gif instance ======')
    instance = GifInstance(
        instanceOperator, 
        # registryAddress=registry_address, 
        instanceWallet=instanceWallet, 
        # publishSource=publish_source
        gif=get_package('gif-contracts'))
        
    
    instanceService = instance.getInstanceService()
    instanceOperatorService = instance.getInstanceOperatorService()
    componentOwnerService = instance.getComponentOwnerService()

    deployment = _add_instance_to_deployment(
        stakeholders_accounts,
        instance)

    print('====== create initial setup ======')

    initialFunding = 100000

    print('2) riskpool wallet {} approval for instance treasury {}'.format(
        riskpoolWallet, instance.getTreasury()))

    erc20Token.approve(instance.getTreasury(), 10 * initialFunding * mult, {'from': riskpoolWallet})

    print('====== deploy and setup creation complete ======')
    print('')

    # check balances at end of setup
    balances_after_setup = _get_balances(stakeholders_accounts)

    print('--------------------------------------------------------------------')
    print('inital balances: {}'.format(balances_before))
    print('after deploy balances: {}'.format(balances_after_deploy))
    print('end of setup balances: {}'.format(balances_after_setup))

    delta_deploy = _get_balances_delta(balances_before, balances_after_deploy)
    delta_setup = _get_balances_delta(balances_after_deploy, balances_after_setup)
    delta_total = _get_balances_delta(balances_before, balances_after_setup)

    print('--------------------------------------------------------------------')
    print('total deploy {}'.format(delta_deploy['total']))
    print('deploy {}'.format(delta_deploy))

    print('--------------------------------------------------------------------')
    print('total setup after deploy {}'.format(delta_setup['total']))
    print('setup after deploy {}'.format(delta_setup))

    print('--------------------------------------------------------------------')
    print('total deploy + setup{}'.format(delta_total['total']))
    print('deploy + setup{}'.format(delta_total))

    print('--------------------------------------------------------------------')

    _pretty_print_delta('gas usage deploy', delta_deploy)
    _pretty_print_delta('gas usage total', delta_total)

    deployment = _add_instance_to_deployment(
        stakeholders_accounts,
        instance)

    deployment[DIP_TOKEN] = dip_token
    deployment[ERC20_PROTECTED_TOKEN] = erc20_protected_token
    deployment[ERC20_TOKEN] = contract_from_address(interface.ERC20, erc20Token)

    deployment[PRODUCT] = contract_from_address(DepegProduct, product)
    deployment[RISKPOOL] = contract_from_address(DepegRiskpool, riskpool)
    deployment[RISKPOOL_WALLET] = riskpoolWallet

    print('deployment: {}'.format(deploy_result))

    return deployment


def _add_tokens_to_deployment(
    deployment,
    usdc
):
    deployment[ERC20_TOKEN] = usdc
    return deployment


def _copy_hashmap(map_in):
    map_out = {}

    for key, value in elements(map_in):
        map_out[key] = value
    
    return map_out


def _add_instance_to_deployment(
    deployment,
    instance
):
    deployment[INSTANCE] = instance
    deployment[INSTANCE_SERVICE] = instance.getInstanceService()
    deployment[INSTANCE_WALLET] = deployment[INSTANCE_SERVICE].getInstanceWallet()

    deployment[INSTANCE_OPERATOR_SERVICE] = instance.getInstanceOperatorService()
    deployment[COMPONENT_OWNER_SERVICE] = instance.getComponentOwnerService()

    return deployment


def _add_product_to_deployment(
    deployment,
    product,
    oracle,
    riskpool
):
    deployment[PRODUCT] = product
    deployment[ORACLE] = oracle
    deployment[RISKPOOL] = riskpool

    return deployment


def all_in_1(
    stakeholders_accounts=None,
    registry_address=None,
    usdc_address=None,
    deploy_all=False,
    disable_staking=True,
    publish_source=False
):
    a = stakeholders_accounts or stakeholders_accounts_ganache()

    # assess balances at beginning of deploy
    balances_before = _get_balances(a)

    # deploy full setup including tokens, and gif instance
    if deploy_all:
        usdc = Usdc.deploy({'from':a[INSTANCE_OPERATOR]}, publish_source=publish_source)
        instance = GifInstance(
            instanceOperator=a[INSTANCE_OPERATOR], 
            instanceWallet=a[INSTANCE_WALLET])

    # where available reuse tokens and gif instgance from existing deployments
    else:
        if usdc_address or get_address('usdc'):
            usdc = contract_from_address(
                interface.IERC20Metadata, 
                dip_address or get_address('usdc'))
        else:
            usdc = Usdc.deploy({'from':a[INSTANCE_OPERATOR]}, publish_source=publish_source)

        instance = GifInstance(
            instanceOperator=a[INSTANCE_OPERATOR], 
            instanceWallet=a[INSTANCE_WALLET],
            registryAddress=registry_address or get_address('registry'))

    print('====== token setup ======')
    print('- usdc {} {}'.format(usdc.symbol(), usdc))

    # populate deployment hashmap
    deployment = _copy_map(a)
    deployment = _add_tokens_to_deployment(deployment, usdc)
    deployment = _add_instance_to_deployment(deployment, instance)

    balances_after_instance_setup = _get_balances(a)

    # deploy and setup for depeg product + riskpool
    instance_service = instance.getInstanceService()

    productOwner = a[PRODUCT_OWNER]
    oracleProvider = a[ORACLE_PROVIDER]
    investor = a[INVESTOR]
    riskpoolKeeper = a[RISKPOOL_KEEPER]
    riskpoolWallet = a[RISKPOOL_WALLET]
    
    print('====== deploy fire product/oracle/riskpool ======')
    fireDeploy = GifFireProductComplete(
        instance,
        productOwner,
        investor,
        usdc,
        oracleProvider,
        riskpoolKeeper,
        riskpoolWallet,
        publishSource=publish_source)

    # assess balances at beginning of deploy
    balances_after_deploy = _get_balances(a)

    fireProduct = fireDeploy.getProduct()
    fireOracle = fireDeploy.getOracle()
    fireRiskpool = fireDeploy.getRiskpool()

    product = fireProduct.getContract()
    oracle = fireOracle.getContract()
    riskpool = fireRiskpool.getContract()

    deployment = _add_product_to_deployment(deployment, product, oracle, riskpool)

    print('--- create riskpool setup ---')
    mult_usdc = 10 ** usdc.decimals()

    # fund riskpool
    initial_funding = 10 ** 6
    bundle_id = create_bundle(
        deployment[INSTANCE],
        deployment[INSTANCE_OPERATOR],
        deployment[INVESTOR],
        deployment[RISKPOOL],
        initial_funding * mult_usdc)

    # approval necessary for payouts or pulling out funds by investor
    usdc.approve(
        instance_service.getTreasuryAddress(),
        10 * initial_funding * mult_usdc,
        {'from': deployment[RISKPOOL_WALLET]})

    print('--- create policy ---')

    # fund customer and create approval to pay premium
    customer_funding = 10 ** 5
    usdc.transfer(a[CUSTOMER1], customer_funding * mult_usdc, {'from': a[INSTANCE_OPERATOR]})
    usdc.approve(instance_service.getTreasuryAddress(), customer_funding * mult_usdc, {'from': a[CUSTOMER1]})

    sum_insured = 10 ** 5
    process_id = apply_for_policy(
        OBJECT_NAME,
        deployment[INSTANCE],
        deployment[INSTANCE_OPERATOR],
        product,
        deployment[CUSTOMER1],
        sum_insured * mult_usdc)

    inspect_bundles(deployment)
    inspect_applications(deployment)

    return (
        deployment[CUSTOMER1],
        deployment[CUSTOMER2],
        deployment[PRODUCT],
        deployment[RISKPOOL],
        deployment[ORACLE],
        deployment[RISKPOOL_WALLET],
        deployment[INVESTOR],
        deployment[ERC20_TOKEN],
        deployment[INSTANCE_SERVICE],
        deployment[INSTANCE_OPERATOR],
        process_id,
        deployment)


def get_address(name):
    if not exists('gif_instance_address.txt'):
        return None
    with open('gif_instance_address.txt') as file:
        for line in file:
            if line.startswith(name):
                t = line.split('=')[1].strip()
                print('found {} in gif_instance_address.txt: {}'.format(name, t))
                return t
    return None


def new_bundle(
    d,
    funding,
) -> int:
    return create_bundle(
        d[INSTANCE],
        d[INSTANCE_OPERATOR],
        d[INVESTOR],
        d[RISKPOOL],
        funding,
        bundleName,
        bundleLifetimeDays,
        minSumInsured,
        maxSumInsured,
        minDurationDays,
        maxDurationDays,
        aprPercentage
    ) 


def new_policy(
    d,
    wallet,
    sumInsured,
    durationDays,
    maxPremium  
) -> str:
    product = d[PRODUCT]
    customer = d[CUSTOMER1]
    duration = durationDays*24*3600
    tx = product.applyForPolicy(wallet, sumInsured, duration, maxPremium, {'from': customer})

    if 'LogDepegApplicationCreated' in tx.events:
        processId = tx.events['LogDepegApplicationCreated']['processId']
    else:
        processId = None

    applicationSuccess = 'success' if processId else 'failed'
    policySuccess = 'success' if 'LogDepegPolicyCreated' in tx.events else 'failed'

    print('processId {} application {} policy {}'.format(
        processId,
        applicationSuccess,
        policySuccess))

    return processId


def inspect_applications(d):
    instanceService = d[INSTANCE_SERVICE]
    product = d[PRODUCT]
    riskpool = d[RISKPOOL]
    usdc = d[ERC20_TOKEN]

    mul_usdc = 10**usdc.decimals()

    processIds = product.applications()

    # print header row
    print('i customer product id type state object premium suminsured')

    # print individual rows
    for idx in range(processIds):
        processId = product.getApplicationId(idx) 
        metadata = instanceService.getMetadata(processId)
        customer = metadata[0]
        productId = metadata[1]

        application = instanceService.getApplication(processId)
        state = application[0]
        premium = application[1]
        suminsured = application[2]
        appdata = application[3]
        (object_name) = product.decodeApplicationParameterFromData(appdata)

        if state == 2:
            policy = instanceService.getPolicy(processId)
            state = policy[0]
            kind = 'policy'
        else:
            policy = None
            kind = 'application'

        print('{} {} {} {} {} {} "{}" {:.1f} {:.1f}'.format(
            idx,
            _shortenAddress(customer),
            productId,
            processId,
            kind,
            state,
            object_name,
            premium/mul_usdc,
            suminsured/mul_usdc,
        ))


def _shortenAddress(address) -> str:
    return '{}..{}'.format(
        address[:5],
        address[-4:])


def get_bundle_data(
    instanceService,
    riskpool
):
    riskpoolId = riskpool.getId()
    activeBundles = riskpool.activeBundles()

    bundleData = []

    for idx in range(activeBundles):
        bundleId = riskpool.getActiveBundleId(idx)
        bundle = instanceService.getBundle(bundleId)

        capital = bundle[5]
        locked = bundle[6]
        capacity = bundle[5]-bundle[6]

        bundleData.append({
            'idx':idx,
            'riskpoolId':riskpoolId,
            'bundleId':bundleId,
            'capital':capital,
            'locked':locked,
            'capacity':capacity
        })

    return bundleData


def inspect_bundles(d):
    instanceService = d[INSTANCE_SERVICE]
    riskpool = d[RISKPOOL]
    usdc = d[ERC20_TOKEN]

    mul_usdc = 10**usdc.decimals()
    bundleData = get_bundle_data(instanceService, riskpool)

    # print header row
    print('i riskpool bundle token capital locked capacity')

    # print individual rows
    for idx in range(len(bundleData)):
        b = bundleData[idx]

        print('{} {} {} {} {:.1f} {:.1f} {:.1f}'.format(
            b['idx'],
            b['riskpoolId'],
            b['bundleId'],
            usdc.symbol(),
            b['capital']/mul_usdc,
            b['locked']/mul_usdc,
            b['capacity']/mul_usdc
        ))


def from_component(
    componentAddress,
    productId=0,
    riskpoolId=0
):
    component = contract_from_address(interface.IComponent, componentAddress)
    return from_registry(component.getRegistry(), productId=productId, riskpoolId=riskpoolId)


def from_registry(
    registryAddress,
    productId=0,
    riskpoolId=0
):
    instance = GifInstance(registryAddress=registryAddress)
    instanceService = instance.getInstanceService()

    products = instanceService.products()
    riskpools = instanceService.riskpools()

    product = None
    riskpool = None

    if products >= 1:
        if productId > 0:
            componentId = productId
        else:
            componentId = instanceService.getProductId(products-1)

            if products > 1:
                print('1 product expected, {} products available'.format(products))
                print('returning last product available')
        
        componentAddress = instanceService.getComponent(componentId)
        product = contract_from_address(DepegProduct, componentAddress)

        if product.getType() != 1:
            product = None
            print('component (type={}) with id {} is not product'.format(product.getType(), componentId))
            print('no product returned (None)')
    else:
        print('1 product expected, no product available')
        print('no product returned (None)')

    if riskpools >= 1:
        if riskpoolId > 0:
            componentId = riskpoolId
        else:
            componentId = instanceService.getRiskpoolId(riskpools-1)

            if riskpools > 1:
                print('1 riskpool expected, {} riskpools available'.format(riskpools))
                print('returning last riskpool available')
        
        componentAddress = instanceService.getComponent(componentId)
        riskpool = contract_from_address(DepegRiskpool, componentAddress)

        if riskpool.getType() != 2:
            riskpool = None
            print('component (type={}) with id {} is not riskpool'.format(component.getType(), componentId))
            print('no riskpool returned (None)')
    else:
        print('1 riskpool expected, no riskpools available')
        print('no riskpool returned (None)')

    return (instance, product, riskpool)


def _copy_map(map_in):
    map_out = {}

    for key, value in map_in.items():
        map_out[key] = value

    return map_out
