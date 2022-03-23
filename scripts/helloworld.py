from brownie.network.account import Account

from brownie import (
    HelloWorldInsurance,
    HelloWorldOracle,
)

from scripts.instance import Instance
from scripts.product import Product

class HelloWorld(Product):

    def __init__(
        self, 
        oracleOwner: Account,
        productOwner: Account,
        instance: Instance,
        publishSource: bool = False
    ):
        super().__init__(
            'HelloWorld', 
            HelloWorldInsurance, 
            productOwner, 
            '(bytes input)', 
            '(bytes1 greetingResponseCode)', 
            HelloWorldOracle,
            oracleOwner,
            instance,
            publishSource)
