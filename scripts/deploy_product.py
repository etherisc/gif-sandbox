from brownie.network import accounts
from brownie.network.account import Account

from brownie import (
    interface,
    network,
    web3,
    Usdc,
)

from scripts.product import GifProductComplete
from scripts.instance import GifInstance

from scripts.util import (
    contract_from_address,
    get_package
)

from os.path import exists

# allowance for claim payouts or staking withdrawals
RISKPOOL_WALLET_ALLOWANCE = 10 ** 32

# instance specific constants
from scripts.const import (
    INSTANCE_OPERATOR,
    INSTANCE_WALLET,
    ORACLE_PROVIDER,
    CHAINLINK_NODE_OPERATOR,
    RISKPOOL_KEEPER,
    RISKPOOL_WALLET,
    INVESTOR,
    PRODUCT_OWNER,
    INSURER,
    CUSTOMER1,
    CUSTOMER2,
    REGISTRY_OWNER,
    STAKER,
    OUTSIDER,
)

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

CHAIN_ID_MUMBAI = 80001
CHAIN_IDS_WITH_GAS_PRICE = [CHAIN_ID_MUMBAI]

# GAS_PRICE = web3.eth.gas_price
# mumbai price estimate
GAS_PRICE = 1600000000
GAS_PRICE_SAFETY_FACTOR = 1.25

GAS_S = 2000000
GAS_M = 3 * GAS_S
GAS_L = 10 * GAS_M

REQUIRED_FUNDS_S = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_S)
REQUIRED_FUNDS_M = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_M)
REQUIRED_FUNDS_L = int(GAS_PRICE * GAS_PRICE_SAFETY_FACTOR * GAS_L)

REQUIRED_FUNDS = {
    INSTANCE_OPERATOR: REQUIRED_FUNDS_L,
    INSTANCE_WALLET:   REQUIRED_FUNDS_S,
    PRODUCT_OWNER:     REQUIRED_FUNDS_M,
    INSURER:           REQUIRED_FUNDS_S,
    ORACLE_PROVIDER:   REQUIRED_FUNDS_M,
    RISKPOOL_KEEPER:   REQUIRED_FUNDS_M,
    RISKPOOL_WALLET:   REQUIRED_FUNDS_S,
    INVESTOR:          REQUIRED_FUNDS_S,
    CUSTOMER1:         REQUIRED_FUNDS_S,
    CUSTOMER2:         REQUIRED_FUNDS_S,
}


def verify_deploy_base(
    from_component,
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
        product_id=product_id,
        oracle_id=oracle_id,
        riskpool_id=riskpool_id
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
    verify_element('ProductContract', product.address, instanceService.getComponent(product_id))
    verify_element('ProductOwner', product.owner(), productOwner)
    verify_element('ProductToken', product.getToken(), erc20_token.address)
    verify_element('ProductOracle', product.getOracleId(), oracle_id)
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
    insurer=accounts[7]
    customer=accounts[8]
    customer2=accounts[9]

    return {
        INSTANCE_OPERATOR: instanceOperator,
        INSTANCE_WALLET: instanceWallet,
        RISKPOOL_KEEPER: riskpoolKeeper,
        RISKPOOL_WALLET: riskpoolWallet,
        INVESTOR: investor,
        ORACLE_PROVIDER: oracleProvider,
        PRODUCT_OWNER: productOwner,
        INSURER: insurer,
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
    gas_price = get_gas_price()
    print('chain id: {}'.format(web3.eth.chain_id))
    print('gas price [Mwei]: {}'.format(gas_price/10**6))
    print('gas price safety factor: {}'.format(GAS_PRICE_SAFETY_FACTOR))

    print('gas S: {}'.format(GAS_S))
    print('gas M: {}'.format(GAS_M))
    print('gas L: {}'.format(GAS_L))

    print('required S [ETH]: {}'.format(REQUIRED_FUNDS_S / 10**18))
    print('required M [ETH]: {}'.format(REQUIRED_FUNDS_M / 10**18))
    print('required L [ETH]: {}'.format(REQUIRED_FUNDS_L / 10**18))


def get_gas_price() -> int:
    if web3.chain_id in CHAIN_IDS_WITH_GAS_PRICE:
        return web3.eth.gas_price
    
    return GAS_PRICE


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


def _add_tokens_to_deployment(
    deployment,
    token
):
    deployment[ERC20_TOKEN] = token
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


def all_in_1_base(
    base_name,
    tokenContractClass,
    productContractClass,
    oracleContractClass,
    riskpoolContractClass,
    create_bundle,
    create_policy,
    stakeholders_accounts=None,
    registry_address=None,
    token_address=None,
    deploy_all=False,
    publish_source=False
):
    a = stakeholders_accounts or stakeholders_accounts_ganache()

    # assess balances at beginning of deploy
    balances_before = _get_balances(a)

    # deploy full setup including tokens, and gif instance
    if deploy_all:
        token = tokenContractClass.deploy({'from':a[INSTANCE_OPERATOR]}, publish_source=publish_source)
        instance = GifInstance(
            instanceOperator=a[INSTANCE_OPERATOR], 
            instanceWallet=a[INSTANCE_WALLET],
            publish_source=publish_source)

    # where available reuse tokens and gif instgance from existing deployments
    else:
        if token_address or get_address('token'):
            token = contract_from_address(
                interface.IERC20Metadata, 
                token_address or get_address('token'))
        else:
            token = tokenContractClass.deploy({'from':a[INSTANCE_OPERATOR]}, publish_source=publish_source)

        instance = GifInstance(
            instanceOperator=a[INSTANCE_OPERATOR], 
            instanceWallet=a[INSTANCE_WALLET],
            registryAddress=registry_address or get_address('registry'),
            publish_source=publish_source)

    print('====== token setup ======')
    print('- token {} {}'.format(token.symbol(), token))

    # populate deployment hashmap
    deployment = _copy_map(a)
    deployment = _add_tokens_to_deployment(deployment, token)
    deployment = _add_instance_to_deployment(deployment, instance)

    balances_after_instance_setup = _get_balances(a)

    # deploy and setup for depeg product + riskpool
    instance_service = instance.getInstanceService()

    instanceOperator = a[INSTANCE_OPERATOR]
    productOwner = a[PRODUCT_OWNER]
    oracleProvider = a[ORACLE_PROVIDER]
    riskpoolKeeper = a[RISKPOOL_KEEPER]
    riskpoolWallet = a[RISKPOOL_WALLET]
    investor = a[INVESTOR]
    customer = a[CUSTOMER1]
    
    print('====== deploy product/oracle/riskpool "{}" ======'.format(base_name))
    gifDeployment = GifProductComplete(
        instance,
        productContractClass,
        oracleContractClass,
        riskpoolContractClass,
        productOwner,
        oracleProvider,
        riskpoolKeeper,
        riskpoolWallet,
        investor,
        token,
        name=base_name,
        publish_source=publish_source)

    # assess balances at beginning of deploy
    balances_after_deploy = _get_balances(a)

    gifProduct = gifDeployment.getProduct()
    gifOracle = gifDeployment.getOracle()
    gifRiskpool = gifDeployment.getRiskpool()

    product = gifProduct.getContract()
    oracle = gifOracle.getContract()
    riskpool = gifRiskpool.getContract()

    deployment = _add_product_to_deployment(deployment, product, oracle, riskpool)

    print('--- create risk bundle and policy ---')

    # approval for payouts or pulling out funds by investor
    token.approve(
        instance_service.getTreasuryAddress(),
        RISKPOOL_WALLET_ALLOWANCE,
        {'from': deployment[RISKPOOL_WALLET]})

    bundle_id = create_bundle(
        instance, 
        instanceOperator,
        riskpool,
        investor)

    process_id = create_policy(
        instance, 
        instanceOperator,
        product,
        customer)

    return (
        deployment[CUSTOMER1],
        deployment[CUSTOMER2],
        deployment[PRODUCT],
        deployment[ORACLE],
        deployment[RISKPOOL],
        deployment[RISKPOOL_WALLET],
        deployment[INVESTOR],
        deployment[ERC20_TOKEN],
        deployment[INSTANCE],
        deployment[INSTANCE_SERVICE],
        deployment[INSTANCE_OPERATOR],
        bundle_id,
        process_id,
        deployment)


def get_riskpool_token(riskpool):
    tokenAddress = riskpool.getErc20Token()
    return contract_from_address(interface.IERC20Metadata, tokenAddress)


def get_product_token(product):
    tokenAddress = product.getToken()
    return contract_from_address(interface.IERC20Metadata, tokenAddress)


def fund_and_create_allowance(
    instance,
    instanceOperator,
    recipient,
    token,
    funding
):
    instanceService = instance.getInstanceService()
    token.transfer(recipient, funding, {'from': instanceOperator})
    token.approve(instanceService.getTreasuryAddress(), funding, {'from': recipient})


def get_bundle_id(tx):
    return tx.events['LogRiskpoolBundleCreated']['bundleId']


def get_process_id(tx):
    return tx.events['LogMetadataCreated']['processId']


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


def inspect_applications(d):
    instanceService = d[INSTANCE_SERVICE]
    product = d[PRODUCT]
    riskpool = d[RISKPOOL]
    token = d[ERC20_TOKEN]

    mult_token = 10**token.decimals()

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

        if state == 2:
            policy = instanceService.getPolicy(processId)
            state = policy[0]
            kind = 'policy'
        else:
            policy = None
            kind = 'application'

        print('{} {} {} {} {} {} {:.1f} {:.1f}'.format(
            idx,
            _shortenAddress(customer),
            productId,
            processId,
            kind,
            state,
            premium/mult_token,
            suminsured/mult_token,
        ))


def _shortenAddress(address) -> str:
    return '{}..{}'.format(
        address[:5],
        address[-4:])


def get_bundle_data(
    instanceService,
    riskpool
):
    bundle_nft = contract_from_address(interface.IERC721, instanceService.getBundleToken())
    active_bundles = riskpool.activeBundles()
    bundle_data = []

    for idx in range(active_bundles):
        bundle_id = riskpool.getActiveBundleId(idx)
        bundle = instanceService.getBundle(bundle_id).dict()

        bundle_data.append({
            'idx':idx,
            'owner':bundle_nft.ownerOf(bundle['tokenId']),
            'riskpoolId':bundle['riskpoolId'],
            'bundleId':bundle_id,
            'capital':bundle['capital'],
            'locked':bundle['lockedCapital'],
            'capacity':bundle['capital'] - bundle['lockedCapital']
        })

    return bundle_data


def inspect_bundles(d):
    instanceService = d[INSTANCE_SERVICE]
    riskpool = d[RISKPOOL]
    token = d[ERC20_TOKEN]

    mult_token = 10 ** token.decimals()
    bundleData = get_bundle_data(instanceService, riskpool)

    # print header row
    print('i owner riskpool bundle token capital locked capacity')

    # print individual rows
    for idx in range(len(bundleData)):
        b = bundleData[idx]

        print('{} {} {} {} {} {:.1f} {:.1f} {:.1f}'.format(
            b['idx'],
            _shortenAddress(b['owner']),
            b['riskpoolId'],
            b['bundleId'],
            token.symbol(),
            b['capital']/mult_token,
            b['locked']/mult_token,
            b['capacity']/mult_token
        ))


def from_component_base(
    component_address,
    product_contract_class,
    oracle_contract_class,
    riskpool_contract_class,
    product_id,
    oracle_id,
    riskpool_id
):
    component = contract_from_address(
        interface.IComponent,
        component_address)

    return from_registry_base(
        component.getRegistry(),
        product_contract_class,
        oracle_contract_class,
        riskpool_contract_class,
        product_id=product_id,
        oracle_id=oracle_id,
        riskpool_id=riskpool_id)


def from_registry_base(
    registryAddress,
    product_contract_class,
    oracle_contract_class,
    riskpool_contract_class,
    product_id=0,
    oracle_id=0,
    riskpool_id=0
):
    instance = GifInstance(registryAddress=registryAddress)
    instance_service = instance.getInstanceService()

    products = instance_service.products()
    oracles = instance_service.oracles()
    riskpools = instance_service.riskpools()

    product = None
    oracle = None
    riskpool = None

    if products >= 1:
        if product_id > 0:
            component_id = product_id
        else:
            component_id = instance_service.getProductId(products-1)

            if products > 1:
                print('1 product expected, {} products available'.format(products))
                print('returning last product available')
        
        component_address = instance_service.getComponent(component_id)
        product = contract_from_address(product_contract_class, component_address)

        if product.getType() != 1:
            product = None
            print('component (type={}) with id {} is not product'.format(product.getType(), component_id))
            print('no product returned (None)')
    else:
        print('1 product expected, no product available')
        print('no product returned (None)')

    if oracles >= 1:
        if oracle_id > 0:
            component_id = oracle_id
        else:
            component_id = instance_service.getOracleId(oracles-1)

            if oracles > 1:
                print('1 oracle expected, {} oraclea available'.format(oracles))
                print('returning last oracle available')
        
        component_address = instance_service.getComponent(component_id)
        oracle = contract_from_address(oracle_contract_class, component_address)

        if oracle.getType() != 0:
            oracle = None
            print('component (type={}) with id {} is not oracle'.format(oracle.getType(), component_id))
            print('no oracle returned (None)')
    else:
        print('1 oracle expected, no oracle available')
        print('no oracle returned (None)')

    if riskpools >= 1:
        if riskpool_id > 0:
            component_id = riskpool_id
        else:
            component_id = instance_service.getRiskpoolId(riskpools-1)

            if riskpools > 1:
                print('1 riskpool expected, {} riskpools available'.format(riskpools))
                print('returning last riskpool available')
        
        component_address = instance_service.getComponent(component_id)
        riskpool = contract_from_address(riskpool_contract_class, component_address)

        if riskpool.getType() != 2:
            riskpool = None
            print('component (type={}) with id {} is not riskpool'.format(component.getType(), component_id))
            print('no riskpool returned (None)')
    else:
        print('1 riskpool expected, no riskpools available')
        print('no riskpool returned (None)')

    return (instance, product, oracle, riskpool)


def to_token_amount(token, amount):
    return amount * 10 ** token.decimals()


def _copy_map(map_in):
    map_out = {}

    for key, value in map_in.items():
        map_out[key] = value

    return map_out
