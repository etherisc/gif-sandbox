import pytest

from brownie import (
    interface,
    Wei,
    Contract, 
    Usdc,
    FireProduct,
    FireOracle,
    FireRiskpool
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

from scripts.product_fire import (
    GifFireProduct,
    GifFireOracle,
    GifFireRiskpool,
    GifFireProductComplete,
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

#=== access to gif-contracts contract classes  =======================#

@pytest.fixture(scope="module")
def gifi(): return get_package('gif-interface')

@pytest.fixture(scope="module")
def gif(): return get_package('gif-contracts')

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
def oracleProvider(accounts) -> Account:
    return get_filled_account(accounts, 8, "1 ether")

@pytest.fixture(scope="module")
def customer(accounts) -> Account:
    return get_filled_account(accounts, 9, "1 ether")

@pytest.fixture(scope="module")
def customer2(accounts) -> Account:
    return get_filled_account(accounts, 10, "1 ether")

@pytest.fixture(scope="module")
def theOutsider(accounts) -> Account:
    return get_filled_account(accounts, 19, "1 ether")

#=== gif instance fixtures ====================================================#

@pytest.fixture(scope="module")
def registry(instanceOperator) -> GifRegistry: return GifRegistry(instanceOperator, None)

@pytest.fixture(scope="module")
def instance(instanceOperator, instanceWallet) -> GifInstance: return GifInstance(instanceOperator, instanceWallet)

@pytest.fixture(scope="module")
def instanceService(instance): return instance.getInstanceService()

#=== stable coin fixtures ============================================#

@pytest.fixture(scope="module")
def usdc(instanceOperator) -> Usdc: return Usdc.deploy({'from': instanceOperator})

#=== fire contracts fixtures ========================================#

@pytest.fixture(scope="module")
def gifFireDeploy(
    instance: GifInstance, 
    productOwner: Account, 
    investor: Account, 
    usdc,
    oracleProvider: Account, 
    riskpoolKeeper: Account, 
    riskpoolWallet: Account
) -> GifFireProductComplete:
    return GifFireProductComplete(
        instance, 
        productOwner, 
        investor,
        usdc,
        oracleProvider, 
        riskpoolKeeper, 
        riskpoolWallet)

@pytest.fixture(scope="module")
def gifFireProduct(gifFireDeploy) -> GifFireProduct: return gifFireDeploy.getProduct()

@pytest.fixture(scope="module")
def product(gifFireProduct) -> FireProduct: return gifFireProduct.getContract()

@pytest.fixture(scope="module")
def oracle(gifFireProduct) -> FireOracle: return gifFireProduct.getOracle().getContract()

@pytest.fixture(scope="module")
def riskpool(gifFireProduct) -> FireRiskpool: return gifFireProduct.getRiskpool().getContract()
