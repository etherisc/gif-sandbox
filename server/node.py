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
from scripts.util import contract_from_address, s2h, get_package, s2b

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

        gif = get_package('gif-contracts')
        registry = contract_from_address(gif.RegistryController, config.registry_address)
        instanceServiceAddress = registry.getContract(s2b('InstanceService'))
        self._instanceService = contract_from_address(gif.InstanceService, instanceServiceAddress)

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

    def getPolicy(self, process_id:str) -> Policy:        
        application = self._instanceService.getApplication(process_id)
        policy = self._instanceService.getPolicy(process_id)
        object_name = self._fireProduct.decodeApplicationParameterFromData(application['data'])
        return Policy(
            id = process_id,
            object_name = object_name,
            premium = application['premiumAmount'] / 10**6,
            premium_paid = policy['premiumPaidAmount'] / 10**6,
            sum_insured = application['sumInsuredAmount'] / 10**6,
            application_state = application['state'],
            policy_state = policy['state'],
            claims_count = policy['claimsCount'],
            payout_amount = policy['payoutAmount'] / 10**6)

    def applyForPolicy(self, object_name:str, object_value:int) -> str:
        tx = self._fireProduct.applyForPolicy(
            object_name, 
            object_value * 10**6, 
            { "from": self._customer })
        process_id = tx.events['LogApplicationCreated'][0]['processId']
        logging.info('processId {}'.format(process_id))
        return process_id

    def expirePolicy(self, processId:str):
        self._fireProduct.expirePolicy(
            processId, 
            { "from" : self._productOwner })
    