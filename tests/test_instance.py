import brownie
import pytest


from scripts.const import (
    GIF_RELEASE,
    REGISTRY_NAME,
    INSTANCE_SERVICE_NAME,
)

from brownie.network.account import Account

from scripts.util import s2b
from scripts.instance import GifInstance

# enforce function isolation for tests below
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_instance_registry(
    instanceOperator: Account,
    instance: GifInstance,
):
    registry = instance.getRegistry()

    assert registry.address == registry.getContract(s2b(REGISTRY_NAME))
    assert registry.getRelease() == s2b(GIF_RELEASE)


def test_instanceservice(
    instanceOperator: Account,
    instance: GifInstance
):
    registry = instance.getRegistry()
    instanceService = instance.getInstanceService()

    assert instanceService.address == registry.getContract(s2b(INSTANCE_SERVICE_NAME))
    assert instanceService.getInstanceOperator() == instanceOperator
