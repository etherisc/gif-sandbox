import pytest

from brownie import (
    interface,
    Wei,
    Contract, 
    USD1,
    USD2,
    USD3,
    UsdcPriceDataProvider,
    DepegProduct,
    DepegRiskpool,
    InstanceRegistry,
    ComponentRegistry,
    BundleRegistry,
    Staking,
    DIP
)

from brownie.network import accounts
from brownie.network.account import Account

from scripts.const import ACCOUNTS_MNEMONIC

from scripts.util import (
    get_account,
    get_package,
)

from scripts.instance import (
    GifRegistry,
    GifInstance,
)

from scripts.depeg_product import (
    GifDepegProduct,
    GifDepegRiskpool,
    GifDepegProductComplete,
)

def get_filled_account(accounts, account_no, funding) -> Account:
    owner = get_account(ACCOUNTS_MNEMONIC, account_no)
    accounts[account_no].transfer(owner, funding)
    return owner

# fixtures with `yield` execute the code that is placed before the `yield` as setup code
# and code after `yield` is teardown code. 
# See https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#yield-fixtures-recommended
@pytest.fixture(autouse=True)
def run_around_tests():
    try:
        yield
        # after each test has finished, execute one trx and wait for it to finish. 
        # this is to ensure that the last transaction of the test is finished correctly. 
    finally:
        accounts[8].transfer(accounts[9], 1)
        # dummy_account = get_account(ACCOUNTS_MNEMONIC, 999)
        # execute_simple_incrementer_trx(dummy_account)

#=== actor account fixtures  ===========================================#

@pytest.fixture(scope="module")
def instanceOperator(accounts) -> Account:
    return get_filled_account(accounts, 0, "1 ether")

@pytest.fixture(scope="module")
def instanceWallet(accounts) -> Account:
    return get_filled_account(accounts, 1, "1 ether")

@pytest.fixture(scope="module")
def riskpoolKeeper(accounts) -> Account:
    return get_filled_account(accounts, 4, "1 ether")

@pytest.fixture(scope="module")
def riskpoolWallet(accounts) -> Account:
    return get_filled_account(accounts, 5, "1 ether")

@pytest.fixture(scope="module")
def investor(accounts) -> Account:
    return get_filled_account(accounts, 6, "1 ether")

@pytest.fixture(scope="module")
def productOwner(accounts) -> Account:
    return get_filled_account(accounts, 7, "1 ether")

@pytest.fixture(scope="module")
def customer(accounts) -> Account:
    return get_filled_account(accounts, 9, "1 ether")

@pytest.fixture(scope="module")
def customer2(accounts) -> Account:
    return get_filled_account(accounts, 10, "1 ether")

@pytest.fixture(scope="module")
def protectedWallet(accounts) -> Account:
    return get_filled_account(accounts, 11, "1 ether")

@pytest.fixture(scope="module")
def protectedWallet2(accounts) -> Account:
    return get_filled_account(accounts, 12, "1 ether")

@pytest.fixture(scope="module")
def registryOwner(accounts) -> Account:
    return get_filled_account(accounts, 13, "1 ether")

@pytest.fixture(scope="module")
def theOutsider(accounts) -> Account:
    return get_filled_account(accounts, 19, "1 ether")



@pytest.fixture(scope="module")
def staker(accounts) -> Account:
    return get_filled_account(accounts, 11, "1 ether")

@pytest.fixture(scope="module")
def staker2(accounts) -> Account:
    return get_filled_account(accounts, 12, "1 ether")

@pytest.fixture(scope="module")
def stakerWithDips(staker, instanceOperator, dip) -> Account:
    dips = 1000000 * 10**dip.decimals()
    dip.transfer(staker, dips, {'from': instanceOperator})
    return staker

@pytest.fixture(scope="module")
def staker2WithDips(staker2, instanceOperator, dip) -> Account:
    dips = 1000000 * 10**dip.decimals()
    dip.transfer(staker2, dips, {'from': instanceOperator})
    return staker2

#=== access to gif-contracts contract classes  =======================#

@pytest.fixture(scope="module")
def gifi(): return get_package('gif-interface')

@pytest.fixture(scope="module")
def gif(): return get_package('gif-contracts')

#=== stable coin fixtures ============================================#

@pytest.fixture(scope="module")
def usd1(instanceOperator) -> USD1: return USD1.deploy({'from': instanceOperator})

@pytest.fixture(scope="module")
def usd2(instanceOperator) -> USD2: return USD2.deploy({'from': instanceOperator})

@pytest.fixture(scope="module")
def usd3(instanceOperator) -> USD3: return USD3.deploy({'from': instanceOperator})

@pytest.fixture(scope="module")
def dip(instanceOperator) -> DIP: return DIP.deploy({'from': instanceOperator})

@pytest.fixture(scope="module")
def testCoin(instanceOperator, gif) -> Contract: return gif.TestCoin.deploy({'from':instanceOperator})

#=== gif instance fixtures ====================================================#

@pytest.fixture(scope="module")
def registry(instanceOperator) -> GifRegistry: return GifRegistry(instanceOperator, None)

@pytest.fixture(scope="module")
def instance(instanceOperator, instanceWallet) -> GifInstance: return GifInstance(instanceOperator, instanceWallet)

@pytest.fixture(scope="module")
def instanceService(instance): return instance.getInstanceService()

#=== depeg deployed contracts fixtures ========================================#

@pytest.fixture(scope="module")
def usdc_feeder(usd1, productOwner) -> UsdcPriceDataProvider: 
    return UsdcPriceDataProvider.deploy(usd1.address, {'from': productOwner})

@pytest.fixture(scope="module")
def gifDepegDeploy(
    instance: GifInstance, 
    productOwner: Account, 
    investor: Account, 
    usdc_feeder,
    usd2: USD2,
    riskpoolKeeper: Account, 
    riskpoolWallet: Account
) -> GifDepegProductComplete:
    return GifDepegProductComplete(
        instance, 
        productOwner, 
        investor,
        usdc_feeder,
        usd2,
        riskpoolKeeper, 
        riskpoolWallet)

@pytest.fixture(scope="module")
def gifDepegProduct(gifDepegDeploy) -> GifDepegProduct: return gifDepegDeploy.getProduct()

@pytest.fixture(scope="module")
def product(gifDepegProduct) -> DepegProduct: return gifDepegProduct.getContract()

@pytest.fixture(scope="module")
def riskpool(gifDepegProduct) -> DepegRiskpool: return gifDepegProduct.getRiskpool().getContract()


#=== staking fixtures ====================================================#

@pytest.fixture(scope="module")
def instanceRegistry(registryOwner) -> InstanceRegistry: 
    return InstanceRegistry.deploy({'from': registryOwner})


@pytest.fixture(scope="module")
def componentRegistry(registryOwner) -> ComponentRegistry: 
    return ComponentRegistry.deploy({'from': registryOwner})


@pytest.fixture(scope="module")
def bundleRegistry(registryOwner) -> BundleRegistry: 
    return BundleRegistry.deploy({'from': registryOwner})


@pytest.fixture(scope="module")
def staking(registryOwner, bundleRegistry) -> BundleRegistry: 
    return Staking.deploy(bundleRegistry, {'from': registryOwner})
