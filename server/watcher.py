import logging

from threading import Thread
from time import sleep
from typing import Dict

from brownie.project.Project import FireOracle

from server.fire import Fire
from server.request import Request
from server.util import getWeb3Contract

class FireOracleWatcher(object):

    def __init__(self, fire:Fire, events:Dict[int, Request]):
        self._events = events
        self.active = True

        contract = getWeb3Contract(FireOracle, fire.oracle.contract.address)
        logMoveFilter = contract.events.LogFireOracleRequest.createFilter(
            fromBlock='latest')

        worker = Thread(
            target=self._eventLoop, 
            args=(logMoveFilter, 1), 
            daemon=True)
    
        worker.start()

    def _eventLoop(self, eventFilter, pollingIntervall):
        while self.active:
            for event in eventFilter.get_new_entries():
                self._handleEvent(event)
        
            sleep(pollingIntervall)

    def _handleEvent(self, event):
        request = Request(
            log_id = '({},{},{})'.format(
                event.blockNumber,
                event.transactionIndex,
                event.logIndex),
            address = event.address,
            event = event.event,
            args = dict(event.args))
        
        requestId = event.args['requestId']
        self._events[requestId] = request

        logging.info('events[{}] = {}'.format(
            requestId, 
            request))