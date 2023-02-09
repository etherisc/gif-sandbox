import brownie
import pytest

from brownie.network.account import Account
from brownie import (
    Usdc,
)

from scripts.util import b2s
from scripts.product import (
    GifProduct,
    GifOracle,
    GifRiskpool,
)

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_print_fixture_objects(
    gifProduct: GifProduct,
    riskpoolWallet: Account,
    token: Usdc,
):
    gifOracle = gifProduct.getOracle()
    gifRiskpool = gifProduct.getRiskpool()

    print('gifProduct {}'.format(gifProduct))
    print('gifOracle {}'.format(gifOracle))
    print('gifRiskpool {}'.format(gifRiskpool))
    print('riskpoolWallet {}'.format(riskpoolWallet))
    print('getToken() {}'.format(gifProduct.getToken()))
    print('token {}'.format(token))

    product = gifProduct.getContract()
    oracle = gifOracle.getContract()
    riskpool = gifRiskpool.getContract()

    print('product {} id {} name {}'.format(
        product,
        product.getId(),
        b2s(product.getName())
    ))

    print('oracle {} id {} name {}'.format(
        oracle,
        oracle.getId(),
        b2s(oracle.getName())
    ))

    print('riskpool {} id {} name {}'.format(
        riskpool,
        riskpool.getId(),
        b2s(riskpool.getName())
    ))


def test_product_deploy(
    instanceService,
    instanceOperator: Account,
    productOwner: Account,
    oracleProvider: Account,
    riskpoolKeeper: Account,
    product,
    oracle,
    riskpool,
    riskpoolWallet: Account,
    token
):
    # check role assignements
    poRole = instanceService.getProductOwnerRole()
    opRole = instanceService.getOracleProviderRole()
    rkRole = instanceService.getRiskpoolKeeperRole()

    assert instanceService.getInstanceOperator() == instanceOperator
    assert instanceService.hasRole(poRole, productOwner)
    assert instanceService.hasRole(opRole, oracleProvider)
    assert instanceService.hasRole(rkRole, riskpoolKeeper)

    # check deployed product, oracle
    assert instanceService.products() == 1
    assert instanceService.oracles() == 1
    assert instanceService.riskpools() == 1

    assert instanceService.getComponent(product.getId()) == product 
    assert instanceService.getComponent(oracle.getId()) == oracle 
    assert instanceService.getComponent(riskpool.getId()) == riskpool 

    # TODO check fee specification once this is available from instanceService

    # check product
    assert product.getToken() == token
    assert product.getRiskpoolId() == riskpool.getId()

    # check riskpool
    assert riskpool.getWallet() == riskpoolWallet
    assert riskpool.getErc20Token() == token
