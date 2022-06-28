import logging
import uuid

from brownie import network
from brownie.network.account import Account

# from scripts.instance import Instance
from server.util import (
    getContract,
    s2b32
)

from brownie.project.Project import (
    interface,
)

class GifInstance(object):

    def __init__(self, registryAddress:Account, owner:Account):
        logging.info('connected to network {}'.format(network.show_active()))        
        logging.info('setting up instance from registry {}'.format(registryAddress))

        self.registry = getContract(interface.IRegistry, registryAddress)
        self.owner = owner

        isAddress = self.registry.getContract(s2b32('InstanceService'))
        self.instanceService = getContract(interface.IInstanceService, isAddress)

        logging.info('validating read access: products {}, oracles {}'.format(
            self.instanceService.products(),
            self.instanceService.oracles(),
        ))

        iosAddress = self.instanceService.getInstanceOperatorService()
        cosAddress = self.instanceService.getComponentOwnerService()        

        logging.info('validating services. ios {} cos {}'.format(
            iosAddress,
            cosAddress
        ))

        self.instanceOperatorService = getContract(interface.IInstanceOperatorService, iosAddress)
        self.componentOwnerService = getContract(interface.IComponentOwnerService, cosAddress)        


class GifProductComponent(object):

    def __init__(self, name:str, owner:Account, instance:GifInstance):
        self.name = name
        self.owner = owner
        self.instance = instance

        logging.info("setting up component '{}' with owner {}".format(name, owner))
    
    @property
    def nameB32(self):
        return s2b32(self.name)


class GifOracle(GifProductComponent):

    def __init__(
        self, 
        productName:str, 
        oracleClass, 
        owner: Account,
        instance:GifInstance,
        publishSource: bool = False
    ):
        super().__init__(
            '{}.Oracle.{}'.format(
                productName, 
                _uuidNamePart()),
            owner,
            instance)
        
        providerRole = instance.instanceService.oracleProviderRole()
        instance.instanceOperatorService.grantRole(
            providerRole, 
            owner, 
            {'from': instance.owner})

        self.oracle = oracleClass.deploy(
            self.nameB32,
            instance.registry,
            {'from': owner},
            publish_source = publishSource)

        instance.componentOwnerService.propose(
            self.oracle,
            {'from': owner}
        )

        logging.info('component self.id {} proposed'.format(
            self.id))

        instance.instanceOperatorService.approve(
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
        oracle:GifOracle,
        owner:Account,
        instance:GifInstance,
        publishSource: bool = False
    ):
        super().__init__(
            '{}.Product.{}'.format(
                productName, 
                _uuidNamePart()),
            owner,
            instance)
                
        ownerRole = instance.instanceService.productOwnerRole()
        instance.instanceOperatorService.grantRole(
            ownerRole, 
            owner, 
            {'from': instance.owner})

        self.product = productClass.deploy(
            self.nameB32,
            instance.registry,
            oracle.id,
            {'from': owner},
            publish_source=publishSource)

        instance.componentOwnerService.propose(
            self.product,
            {'from': owner}
        )

        instance.instanceOperatorService.approve(
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
        productName:str,
        productClass,
        productOwner:Account,
        oracleClass,
        oracleOwner:Account,
        instance:GifInstance,
        publishSource:bool = False
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

def _uuidNamePart():
    return str(uuid.uuid4())[:8]