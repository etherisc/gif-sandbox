#!/bin/bash

.devcontainer/scripts/deploy-gif.sh 

echo '>>>> Compiling sandbox contracts ...'
echo "" > .env 
rm -rf build/
brownie compile --all 

echo '>>>> Sandbox ready - GIF Registry address in gif_instance_address.txt'
