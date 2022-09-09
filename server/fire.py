import logging

from threading import Thread
from time import sleep
from typing import List

from brownie import network
from brownie.network.contract import Contract
from brownie.network.web3 import web3

from brownie.project.Project import FireInsurance, FireOracle, FireRiskpool

from server.account import Account
from server.product import GifInstance, Product
from server.request import Request

class Fire(Product):

    NETWORK_NAME = 'ganache'

    def __init__(
        self, 
        oracleOwner: Account,
        productOwner: Account,
        riskpoolToken: Account,
        riskpoolWallet: Account,
        investor: Account,
        instance: GifInstance, 
        networkName:str = NETWORK_NAME,
        publishSource:bool = False
    ):
        super().__init__(
            'Fire', 
            FireInsurance, 
            productOwner, 
            FireOracle,
            oracleOwner,
            FireRiskpool,
            riskpoolToken,
            riskpoolWallet,
            investor,
            instance,
            publishSource)

    def info(self) -> str:
        return '<ul>'\
            '<li>Product contract {}</li>'\
            '<li>Oracle contract {}</li>'\
            '<li>Network \'{}\'</li>'\
            '</ul>'.format(
                self.product.contract.address,
                self.oracle.contract.address,
                network.show_active())

    def applyForPolicy(self, objectName:str, premium:int, customer:Account):
        logging.info('applyForPolicy({}, {})'.format(
            objectName, premium, customer.address))

        tx = self.product.contract.applyForPolicy(
            objectName, 
            {
                'from': customer, 
                'value': premium
            })
        
        (policyId, requestId) = tx.return_value
        return (policyId, requestId)


    def expirePolicy(self, policyId:bytes, customer: Account):
        logging.info('expirePolicy({})'.format(policyId))
        
        self.product.contract.expirePolicy(
            policyId, 
            { 'from': customer })
    
    def respondToOracleRequest(self, 
        requestId:int, 
        fireCategory:str, 
        oracleOwner: Account
    ):
        logging.info('respondToOracleRequest({}, {})'.format(
            requestId, fireCategory))
        
        self.oracle.contract.respond(
            requestId, 
            ord(fireCategory),
            {'from': oracleOwner})
