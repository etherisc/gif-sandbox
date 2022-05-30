from brownie.network.account import Account

from brownie import (
    FireInsurance,
    FireOracle,
)

from scripts.instance import Instance
from scripts.product import Product

class Fire(Product):

    def __init__(
        self, 
        oracleOwner: Account,
        productOwner: Account,
        instance: Instance,
        publishSource: bool = False
    ):
        super().__init__(
            'Fire', 
            FireInsurance, 
            productOwner, 
            FireOracle,
            oracleOwner,
            instance,
            publishSource)
