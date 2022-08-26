#!/bin/bash

echo ">>>> Preparing GIF deployment in local ganache chain. Please wait..."
brownie networks add Local ganache host=http://ganache:7545 chainid=1234

export GIF=/gif-contracts

# checkout gif and compile it
echo ">>>> Checking out GIF contracts..."
git clone git@github.com:etherisc/gif-contracts.git $GIF
cd $GIF

echo ">>>> Compiling GIF contracts..."
brownie compile --all
echo "" > .env

# deploy gif and save registry address
echo "Deploying GIF contracts..."
brownie console --network=ganache <<EOF
from scripts.instance import GifInstance
instance = GifInstance(accounts[0], accounts[1])
f = open("/workspace/gif_instance_address.txt", "w")
f.writelines("registry=%s" % (instance.getRegistry().address))
f.close()
EOF

echo ">>>> GIF deployment completed. Registry address is saved in gif_instance_address.txt"
