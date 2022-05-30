from brownie.network.account import Account

from scripts.instance import Instance
from scripts.util import s2b32


class GifProductComponent(object):

    def __init__(self, name:str, owner: Account, instance: Instance):
        self.name = name
        self.owner = owner
        self.instance = instance
    
    @property
    def nameB32(self):
        return s2b32(self.name)


class GifOracle(GifProductComponent):

    def __init__(
        self, 
        productName:str, 
        oracleClass, 
        owner: Account,
        instance: Instance,
        publishSource: bool = False
    ):
        super().__init__(
            '{}.Oracle.{}'.format(
                productName, 
                instance.contract.oracles()),
            owner,
            instance)
        
        self.oracle = oracleClass.deploy(
            instance.contract.getOracleService(),
            instance.contract.getOracleOwnerService(),
            self.nameB32,
            {'from': owner},
            publish_source = publishSource)

        instance.ios.approveOracle(
            self.id, 
            {'from': instance.owner})

    @property
    def id(self):
        return self.oracle.getId()

    @property
    def contract(self):
        return self.oracle


class GifProduct(GifProductComponent):

    def __init__(
        self, 
        productName:str, 
        productClass, 
        oracle: GifOracle,
        owner: Account,
        instance: Instance,
        publishSource: bool = False
    ):
        super().__init__(
            '{}.Product.{}'.format(
                productName, 
                instance.contract.products()),
            owner,
            instance)
        
        self.product = productClass.deploy(
            instance.contract.getProductService(),
            self.nameB32,
            oracle.id,
            {'from': owner},
            publish_source=publishSource)

        instance.ios.approveProduct(
            self.id, 
            {'from': instance.owner})

    @property
    def id(self):
        return self.product.getId()

    @property
    def contract(self):
        return self.product


class Product(object):

    def __init__(
        self, 
        productName: str,
        productClass,
        productOwner: Account,
        oracleClass,
        oracleOwner: Account,
        instance: Instance,
        publishSource: bool = False
    ):

        self.oracle = GifOracle(
            productName, 
            oracleClass,
            oracleOwner,
            instance, 
            publishSource)
        
        self.product = GifProduct(
            productName, 
            productClass, 
            self.oracle, 
            productOwner, 
            instance,
            publishSource)

    @property
    def id(self):
        return self.product.id

    @property
    def contract(self):
        return self.product.contract
