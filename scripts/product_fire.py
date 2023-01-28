import time

from web3 import Web3

from brownie.network.account import Account

from brownie import (
    interface,
    Wei,
    Contract, 
    FireProduct,
    FireOracle,
    FireRiskpool,
)

from scripts.util import s2b
from scripts.instance import GifInstance


class GifFireOracle(object):

    def __init__(self, 
        instance: GifInstance, 
        oracleProvider: Account, 
        name, 
        publishSource=False
    ):
        instanceService = instance.getInstanceService()
        instanceOperatorService = instance.getInstanceOperatorService()
        componentOwnerService = instance.getComponentOwnerService()

        print('------ setting up oracle ------')

        oracleProviderRole = instanceService.getOracleProviderRole()
        print('1) grant oracle provider role {} to oracle provider {}'.format(
            oracleProviderRole, oracleProvider))

        instanceOperatorService.grantRole(
            oracleProviderRole, 
            oracleProvider, 
            {'from': instance.getOwner()})

        print('2) deploy oracle {} by oracle provider {}'.format(
            name, oracleProvider))

        self.oracle = FireOracle.deploy(
            s2b(name),
            instance.getRegistry(),
            {'from': oracleProvider},
            publish_source=publishSource)
        
        print('3) oracle {} proposing to instance by oracle provider {}'.format(
            self.oracle, oracleProvider))
        
        componentOwnerService.propose(
            self.oracle,
            {'from': oracleProvider})

        print('4) approval of oracle id {} by instance operator {}'.format(
            self.oracle.getId(), instance.getOwner()))
        
        instanceOperatorService.approve(
            self.oracle.getId(),
            {'from': instance.getOwner()})
    
    def getId(self) -> int:
        return self.oracle.getId()
    
    def getContract(self) -> FireOracle:
        return self.oracle


class GifFireRiskpool(object):

    def __init__(self, 
        instance: GifInstance, 
        erc20Token: Account,
        riskpoolKeeper: Account, 
        riskpoolWallet: Account,
        investor: Account,
        collateralization:int,
        name, 
        publishSource=False
    ):
        instanceService = instance.getInstanceService()
        instanceOperatorService = instance.getInstanceOperatorService()
        componentOwnerService = instance.getComponentOwnerService()

        print('------ setting up riskpool ------')

        riskpoolKeeperRole = instanceService.getRiskpoolKeeperRole()
        print('1) grant riskpool keeper role {} to riskpool keeper {}'.format(
            riskpoolKeeperRole, riskpoolKeeper))

        instanceOperatorService.grantRole(
            riskpoolKeeperRole, 
            riskpoolKeeper, 
            {'from': instance.getOwner()})

        print('2) deploy riskpool {} by riskpool keeper {}'.format(
            name, riskpoolKeeper))

        sumOfSumInsuredCap = 1000000 * 10 ** 6
        self.riskpool = FireRiskpool.deploy(
            s2b(name),
            sumOfSumInsuredCap,
            erc20Token,
            riskpoolWallet,
            instance.getRegistry(),
            {'from': riskpoolKeeper},
            publish_source=publishSource)
        
        print('3) riskpool {} proposing to instance by riskpool keeper {}'.format(
            self.riskpool, riskpoolKeeper))
        
        componentOwnerService.propose(
            self.riskpool,
            {'from': riskpoolKeeper})

        print('4) approval of riskpool id {} by instance operator {}'.format(
            self.riskpool.getId(), instance.getOwner()))
        
        instanceOperatorService.approve(
            self.riskpool.getId(),
            {'from': instance.getOwner()})

        maxActiveBundles = 10
        print('5) set max number of bundles to {} by riskpool keeper {}'.format(
            maxActiveBundles, riskpoolKeeper))
        
        self.riskpool.setMaximumNumberOfActiveBundles(
            maxActiveBundles,
            {'from': riskpoolKeeper})

        print('6) riskpool wallet {} set for riskpool id {} by instance operator {}'.format(
            riskpoolWallet, self.riskpool.getId(), instance.getOwner()))
        
        instanceOperatorService.setRiskpoolWallet(
            self.riskpool.getId(),
            riskpoolWallet,
            {'from': instance.getOwner()})

        # 7) setup capital fees
        fixedFee = 0
        fractionalFee = 0 # corresponds to 0%
        print('7) creating capital fee spec (fixed: {}, fractional: {}) for riskpool id {} by instance operator {}'.format(
            fixedFee, fractionalFee, self.riskpool.getId(), instance.getOwner()))
        
        feeSpec = instanceOperatorService.createFeeSpecification(
            self.riskpool.getId(),
            fixedFee,
            fractionalFee,
            b'',
            {'from': instance.getOwner()}) 

        print('8) setting capital fee spec by instance operator {}'.format(
            instance.getOwner()))
        
        instanceOperatorService.setCapitalFees(
            feeSpec,
            {'from': instance.getOwner()}) 
    
    def getId(self) -> int:
        return self.riskpool.getId()
    
    def getContract(self) -> FireRiskpool:
        return self.riskpool


class GifFireProduct(object):

    def __init__(self,
        instance: GifInstance,
        erc20Token: Account,
        productOwner: Account,
        oracle: GifFireOracle,
        riskpool: GifFireRiskpool,
        name,
        publishSource=False
    ):
        self.oracle = oracle
        self.riskpool = riskpool
        self.token = erc20Token

        instanceService = instance.getInstanceService()
        instanceOperatorService = instance.getInstanceOperatorService()
        componentOwnerService = instance.getComponentOwnerService()
        registry = instance.getRegistry()

        print('------ setting up product ------')

        productOwnerRole = instanceService.getProductOwnerRole()
        print('1) grant product owner role {} to product owner {}'.format(
            productOwnerRole, productOwner))

        instanceOperatorService.grantRole(
            productOwnerRole,
            productOwner, 
            {'from': instance.getOwner()})

        print('2) deploy product by product owner {}'.format(
            productOwner))
        
        self.product = FireProduct.deploy(
            s2b(name),
            erc20Token.address,
            oracle.getId(),
            riskpool.getId(),
            registry,
            {'from': productOwner},
            publish_source=publishSource)

        print('3) product {} proposing to instance by product owner {}'.format(
            self.product, productOwner))
        
        componentOwnerService.propose(
            self.product,
            {'from': productOwner})

        print('4) approval of product id {} by instance operator {}'.format(
            self.product.getId(), instance.getOwner()))
        
        instanceOperatorService.approve(
            self.product.getId(),
            {'from': instance.getOwner()})

        print('5) setting erc20 product token {} for product id {} by instance operator {}'.format(
            erc20Token, self.product.getId(), instance.getOwner()))

        instanceOperatorService.setProductToken(
            self.product.getId(), 
            erc20Token,
            {'from': instance.getOwner()}) 

        fixedFee = 0
        fractionalFee = instanceService.getFeeFractionFullUnit() / 10 # corresponds to 10%
        print('6) creating premium fee spec (fixed: {}, fractional: {}) for product id {} by instance operator {}'.format(
            fixedFee, fractionalFee, self.product.getId(), instance.getOwner()))
        
        feeSpec = instanceOperatorService.createFeeSpecification(
            self.product.getId(),
            fixedFee,
            fractionalFee,
            b'',
            {'from': instance.getOwner()}) 

        print('7) setting premium fee spec by instance operator {}'.format(
            instance.getOwner()))

        instanceOperatorService.setPremiumFees(
            feeSpec,
            {'from': instance.getOwner()}) 

    
    def getId(self) -> int:
        return self.product.getId()

    def getToken(self):
        return self.token

    def getOracle(self) -> GifFireOracle:
        return self.oracle

    def getRiskpool(self) -> GifFireRiskpool:
        return self.riskpool
    
    def getContract(self) -> FireProduct:
        return self.product


class GifFireProductComplete(object):

    def __init__(self,
        instance: GifInstance,
        productOwner: Account,
        investor: Account,
        erc20Token: Account,
        oracleProvider: Account,
        riskpoolKeeper: Account,
        riskpoolWallet: Account,
        baseName='Fire' + str(int(time.time())),  # FIXME
        publishSource=False
    ):
        instanceService = instance.getInstanceService()
        instanceOperatorService = instance.getInstanceOperatorService()
        componentOwnerService = instance.getComponentOwnerService()
        registry = instance.getRegistry()

        self.token = erc20Token

        self.oracle = GifFireOracle(
            instance, 
            oracleProvider, 
            '{}Oracle'.format(baseName),
            publishSource)

        self.riskpool = GifFireRiskpool(
            instance, 
            erc20Token, 
            riskpoolKeeper, 
            riskpoolWallet, 
            investor, 
            instanceService.getFullCollateralizationLevel(),
            '{}Riskpool'.format(baseName),
            publishSource)

        self.product = GifFireProduct(
            instance,
            erc20Token, 
            productOwner, 
            self.oracle,
            self.riskpool,
            '{}Product'.format(baseName),
            publishSource)

    def getToken(self):
        return self.token

    def getOracle(self) -> GifFireOracle:
        return self.oracle

    def getRiskpool(self) -> GifFireRiskpool:
        return self.riskpool

    def getProduct(self) -> GifFireProduct:
        return self.product
