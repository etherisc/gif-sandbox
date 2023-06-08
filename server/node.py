import logging

from typing import Dict, List

from brownie.project.Project import FireProduct, FireOracle

from server.account import Account
from server.category import FireCategory
from server.config import Config, PostConfig
from server.fire import Fire
from server.policy import Policy
from server.product import GifInstance
from server.request import Request, Response
from server.watcher import FireOracleWatcher
from scripts.util import contract_from_address, s2h

class Node(object):

    # account numbers for sandbox accounts derived from config mnemonic
    INSTANCE_OWNER = 0
    ORACLE_OWNER = 5
    PRODUCT_OWNER = 6
    CUSTOMER = 8

    # initial capitalization of fire insurance product in wei
    INITIAL_CAPITALIZATION = 10**6
    
    def __init__(self):
        self._policies:Dict[str, Policy] = {}
        self._requests:Dict[int, Request] = {}
        self._config:Config = None
        self._instance = None
        self._fireProduct = None
        self._fireOracle = None
        self._registryAddress = None
        self._productAddress = None
        self._oracleAddress = None
    
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
        self._registryAddress = config.registry_address
        logging.info('access gif instance via registry at {}'.format(
            self._registryAddress))
        self._productAddress = config.product_address
        logging.info('access fire insurance product at {}'.format(
            self._productAddress))
        self._oracleAddress = config.oracle_address
        logging.info('access fire oracle at {}'.format(
            self._oracleAddress))
        
        self._fireProduct = contract_from_address(FireProduct, config.product_address)
        self._fireOracle = contract_from_address(FireOracle, config.oracle_address)

        # create config for config get requests
        self._config = Config(
            registry_address = config.registry_address,
            product_address = config.product_address,
            oracle_address = config.oracle_address,
            mnemonic = config.mnemonic,
            product_account_no = Node.PRODUCT_OWNER,
            oracle_account_no = Node.ORACLE_OWNER,
            customer_account_no = Node.CUSTOMER)

    @property
    def requests(self) -> int:
        return self._fireOracle.requestIds()

    def getRequest(self, objectName:str) -> int:
        return self._fireOracle.requestId(objectName)
    
    def sendResponse(self, requestId:int, fireCategory:FireCategory):        
        self._fireOracle.respond(
            requestId, 
            s2h(fireCategory),
            { "from" : self._oracleOwner })
    
    @property
    def policies(self) -> List[Policy]:
        return list(self._policies.values())

    def getPolicy(self, policyId:str) -> Policy:
        if policyId not in self._policies:
            raise ValueError('no policy with id {} available'.format(policyId))
        
        return self._policies[policyId]

    def applyForPolicy(self, objectName:str, premium:int) -> str:
        (policyId, requestId) = self._fire.applyForPolicy(
            objectName, 
            premium, 
            self._customer)
        
        policy = Policy(
            id = str(policyId),
            object_name = objectName,
            request_id = requestId,
            premium = premium,
            sum_insured = 100 * premium,
            expired = False)
        
        logging.info('policy {}'.format(policy))
        self._policies[policy.id] = policy

        return policy.id

    def expirePolicy(self, policyId:str):
        if policyId not in self._policies:
            raise ValueError('no policy with id {} available'.format(policyId))
        
        self._fire.expirePolicy(
            policyId, 
            self._customer)
        
        self._policies[policyId].expired = True
