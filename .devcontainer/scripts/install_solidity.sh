#!/usr/bin/env bash

mkdir -p /home/vscode/.solcx/

if [[ $(uname -m) == 'aarch64' ]]; then
    wget -O /home/vscode/.solcx/solc-v0.8.2 https://github.com/nikitastupin/solc/raw/main/linux/aarch64/solc-v0.8.2
    wget -O /home/vscode/.solcx/solc-v0.8.20 https://github.com/nikitastupin/solc/raw/main/linux/aarch64/solc-v0.8.20
else
    wget -O /home/vscode/.solcx/solc-v0.8.2 https://binaries.soliditylang.org/linux-amd64/solc-linux-amd64-v0.8.2+commit.661d1103
    wget -O /home/vscode/.solcx/solc-v0.8.20 https://github.com/ethereum/solidity/releases/download/v0.8.20/solc-static-linux
fi

chmod 755 /home/vscode/.solcx/solc*
