import logging

from typing import Dict, List

from server.account import Account
from server.category import FireCategory
from server.config import Config, PostConfig
from server.fire import Fire
from server.policy import Policy
from server.product import GifInstance
from server.request import Request
from server.watcher import FireOracleWatcher

class Node(object):

    # account numbers for sandbox accounts derived from config mnemonic
    INSTANCE_OWNER = 0
    ORACLE_OWNER =1
    PRODUCT_OWNER = 2
    CUSTOMER = 3

    # initial capitalization of fire insurance product in wei
    INITIAL_CAPITALIZATION = 10**6
    
    def __init__(self):
        self._policies:Dict[str, Policy] = {}
        self._requests:Dict[int, Request] = {}
        self._config:Config = None
        self._instance = None
        self._fire = None

    def info(self) -> str:
        fireInfo = ''

        if self._fire:
            fireInfo = self._fire.info()
        
        return 'Simple API server to interact with "Fire Insurance" '
        + 'product of the GIF sandbox setup.'
        + fireInfo
    
    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, config:PostConfig):
        self._policies = {}
        self._requests = {}

        # set up accounts
        logging.info('setting up accounts')
        account = Account(config.mnemonic)
        self._instanceOwner = account.getBrownieAccount(Node.INSTANCE_OWNER)
        self._oracleOwner = account.getBrownieAccount(Node.ORACLE_OWNER)
        self._productOwner = account.getBrownieAccount(Node.PRODUCT_OWNER)
        self._customer = account.getBrownieAccount(Node.CUSTOMER)

        # set up gif instance
        registryAddress = config.registry_address
        logging.info('access gif instance via registry at {}'.format(
            registryAddress))

        self._instance = GifInstance(
            registryAddress, 
            self._instanceOwner)

        # deploy fire product on gif instance
        logging.info('deploying fire insurance product')
        self._fire = Fire(
            self._oracleOwner,
            self._productOwner,
            self._instance)

        # capitalisation of product contract
        logging.info('initial capitalization by product owner with {} wei'.format(
            Node.INITIAL_CAPITALIZATION))
        
        self._fire.product.contract.deposit({
            'from': self._productOwner,
            'amount': Node.INITIAL_CAPITALIZATION})

        logging.info('setting up log event watcher')
        watcher = FireOracleWatcher(self._fire, self._requests)

        # create config for config get requests
        self._config = Config(
            product_address = self._fire.product.contract.address,
            oracle_address = self._fire.oracle.contract.address,
            mnemonic = config.mnemonic,
            product_account_no = Node.PRODUCT_OWNER,
            oracle_account_no = Node.ORACLE_OWNER,
            customer_account_no = Node.CUSTOMER)

    @property
    def requests(self) -> List[Request]:
        return list(self._requests.values())

    def getRequest(self, requestId:int) -> Request:
        if requestId not in self._requests:
            raise ValueError('no request with id {} available'.format(requestId))
        
        return self._requests[requestId]
    
    def sendResponse(self, requestId:int, fireCategory:FireCategory):
        if requestId not in self._requests:
            raise ValueError('no request with id {} available'.format(requestId))
        
        self._fire.respondToOracleRequest(
            requestId, 
            fireCategory,
            self._oracleOwner)

        self._requests[requestId].fire_category = fireCategory
        self._requests[requestId].open = False
    
    @property
    def policies(self) -> List[Policy]:
        return list(self._policies.values())

    def getPolicy(self, policyId:str) -> Policy:
        if policyId not in self._policies:
            raise ValueError('no policy with id {} available'.format(policyId))
        
        return self._policies[policyId]

    def applyForPolicy(self, objectName:str, premium:int) -> Policy:
        (policyId, requestId) = self._fire.applyForPolicy(
            objectName, 
            premium, 
            self._customer)
        
        policy = Policy(
            id = str(policyId),
            object_name = objectName,
            request_id = requestId,
            premium = premium,
            sum_insured = 100 * premium)
        
        logging.info('policy {}'.format(policy))
        self._policies[policy.id] = policy

        return policy

    def expirePolicy(self, policyId:str):
        if policyId not in self._policies:
            raise ValueError('no policy with id {} available'.format(policyId))
        
        self._fire.expirePolicy(
            policyId, 
            self._customer)