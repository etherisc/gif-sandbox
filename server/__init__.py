import logging

# setup to allow importing smart contract classes
from brownie import project
p = project.load('.', name='Project')
p.load_config()

# connect to ganache network
from brownie import network
if not network.is_connected():
    network.connect('ganache')

logging.getLogger().setLevel(logging.INFO)
