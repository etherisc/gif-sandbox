![Build](https://github.com/etherisc/depeg-contracts/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![](https://dcbadge.vercel.app/api/server/cVsgakVG4R?style=flat)](https://discord.gg/Qb6ZjgE8)

# Fire Insurance Demo

This repository holds the smart contracts for a demo fire insurance.

## Product Considerations


## Risk Capital Considerations

## Github actions

Only go through the process described here if an updated GIF is required for the deployment test.

### Update Ganache DB for deployment test

Start a local ganache with db folder

```bash
rm -rf .github/workflows/ganache-gif/
ganache-cli \
    --mnemonic "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat" \
    --chain.chainId 1234 \
    --port 7545 \
    --accounts 20 \
    -h "0.0.0.0" \
    --database.dbPath .github/workflows/ganache-gif/
```
In new shell run the following commands

```bash
brownie networks add Local ganache-ghaction host=http://localhost:7545 chainid=1234
cd /gif-contracts
rm -rf build/
brownie console --network=ganache-ghaction
```

Now paste this into the brownie console

```python
from brownie import TestCoin
instanceOperator = accounts[0]
instanceWallet = accounts[1]
usdc = TestCoin.deploy({'from': instanceOperator})
from scripts.instance import GifInstance
instance = GifInstance(instanceOperator, instanceWallet)
print('registry {}\nerc20 {}'.format(
    instance.getRegistry().address,
    usdc.address))
```

Now shutdown above started Ganache chain (ctrl+c) and commit the new files to git. 

Also save the values for registry and erc20 in `scripts/test_deployment.py`. 

