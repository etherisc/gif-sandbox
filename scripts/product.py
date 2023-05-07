import time

from brownie.network.account import Account

from brownie import (
    interface,
    Wei,
    Contract, 
)
from scripts.util import s2b
from scripts.instance import GifInstance

# product contract names
NAME_DEFAULT = 'Protection'

# fees

# 10% fee on premium paid
PREMIUM_FEE_FIXED_DEFAULT = 0
PREMIUM_FEE_FRACTIONAL_DEFAULT = 0.1

# zero fee for staked capital
CAPITAL_FEE_FIXED_DEFAULT = 0
CAPITAL_FEE_FRACTIONAL_DEFAULT = 0

# riskpool risk bundle setup
SUM_OF_SUM_INSURED_CAP_DEFAULT = 1000000
MAX_ACTIVE_RISKPOOL_BUNDLES_DEFAULT = 10


class GifOracle(object):

    def __init__(self, 
        instance: GifInstance, 
        oracleContractClass,
        oracleProvider: Account, 
        name,
        publish_source
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

        self.oracle = oracleContractClass.deploy(
            s2b(name),
            instance.getRegistry(),
            {'from': oracleProvider},
            publish_source=publish_source)
        
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
    
    def getContract(self):
        return self.oracle


class GifRiskpool(object):

    def __init__(self, 
        instance: GifInstance, 
        riskpoolContractClass,
        riskpoolKeeper: Account, 
        name, 
        erc20Token: Account,
        riskpoolWallet: Account,
        investor: Account,
        collateralization:int,
        publish_source,
        sumOfSumInsuredCap=SUM_OF_SUM_INSURED_CAP_DEFAULT,
        maxActiveBundles=MAX_ACTIVE_RISKPOOL_BUNDLES_DEFAULT,
        fixedFee=CAPITAL_FEE_FIXED_DEFAULT,
        fractionalFee=CAPITAL_FEE_FRACTIONAL_DEFAULT
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

        self.riskpool = riskpoolContractClass.deploy(
            s2b(name),
            collateralization,
            erc20Token,
            riskpoolWallet,
            instance.getRegistry(),
            {'from': riskpoolKeeper},
            publish_source=publish_source)
        
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
        print('7) creating capital fee spec (fixed: {}, fractional: {}) for riskpool id {} by instance operator {}'.format(
            fixedFee, fractionalFee, self.riskpool.getId(), instance.getOwner()))
        
        feeSpec = instanceOperatorService.createFeeSpecification(
            self.riskpool.getId(),
            fixedFee,
            fractionalFee * instanceService.getFeeFractionFullUnit(),
            b'',
            {'from': instance.getOwner()}) 

        print('8) setting capital fee spec by instance operator {}'.format(
            instance.getOwner()))
        
        instanceOperatorService.setCapitalFees(
            feeSpec,
            {'from': instance.getOwner()}) 
    
    def getId(self) -> int:
        return self.riskpool.getId()
    
    def getContract(self):
        return self.riskpool


class GifProduct(object):

    def __init__(self,
        instance: GifInstance,
        productContractClass,
        productOwner: Account,
        name, 
        erc20Token: Account,
        oracle: GifOracle,
        riskpool: GifRiskpool,
        publish_source,
        fixedFee=PREMIUM_FEE_FIXED_DEFAULT,
        fractionalFee=PREMIUM_FEE_FRACTIONAL_DEFAULT,
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

        print('2) deploy product {} by product owner {}'.format(
            name, productOwner))
        
        self.product = productContractClass.deploy(
            s2b(name),
            erc20Token.address,
            oracle.getId(),
            riskpool.getId(),
            registry,
            {'from': productOwner},
            publish_source=publish_source)

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

        print('6) creating premium fee spec (fixed: {}, fractional: {}) for product id {} by instance operator {}'.format(
            fixedFee, fractionalFee, self.product.getId(), instance.getOwner()))
        
        feeSpec = instanceOperatorService.createFeeSpecification(
            self.product.getId(),
            fixedFee,
            fractionalFee * instanceService.getFeeFractionFullUnit(),
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

    def getOracle(self) -> GifOracle:
        return self.oracle

    def getRiskpool(self) -> GifRiskpool:
        return self.riskpool
    
    def getContract(self):
        return self.product


class GifProductComplete(object):

    def __init__(self,
        instance: GifInstance,
        productContractClass,
        oracleContractClass,
        riskpoolContractClass,
        productOwner: Account,
        oracleProvider: Account,
        riskpoolKeeper: Account,
        riskpoolWallet: Account,
        investor: Account,
        erc20Token: Account,
        name=NAME_DEFAULT,  
        publish_source=False
    ):
        instanceService = instance.getInstanceService()
        instanceOperatorService = instance.getInstanceOperatorService()
        componentOwnerService = instance.getComponentOwnerService()
        registry = instance.getRegistry()

        self.token = erc20Token
        baseName = '{}_{}'.format(name, str(int(time.time()))) # FIXME

        self.oracle = GifOracle(
            instance,
            oracleContractClass,
            oracleProvider, 
            '{}_Oracle'.format(baseName),
            publish_source)

        self.riskpool = GifRiskpool(
            instance, 
            riskpoolContractClass,
            riskpoolKeeper, 
            '{}_Riskpool'.format(baseName),
            erc20Token, 
            riskpoolWallet, 
            investor, 
            instanceService.getFullCollateralizationLevel(),
            publish_source)

        self.product = GifProduct(
            instance,
            productContractClass,
            productOwner, 
            '{}_Product'.format(baseName),
            erc20Token, 
            self.oracle,
            self.riskpool,
            publish_source)

    def getToken(self):
        return self.token

    def getOracle(self) -> GifOracle:
        return self.oracle

    def getRiskpool(self) -> GifRiskpool:
        return self.riskpool

    def getProduct(self) -> GifProduct:
        return self.product
