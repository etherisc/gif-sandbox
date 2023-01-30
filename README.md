![Build](https://github.com/etherisc/depeg-contracts/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![](https://dcbadge.vercel.app/api/server/cVsgakVG4R?style=flat)](https://discord.gg/Qb6ZjgE8)

# Fire Insurance Demo

This repository holds the smart contracts for a demo fire insurance.

## Setup Assumptions

1. Developing with VS Code
2. Working with dev containers

## TODO Fix Server to interact with contracts

current state does not work, not recommended to use/modify
if this is needed short/mid term ping us on discord.

## Interaction via Command Line

### Running Unit Tests

```bash
brownie test -n 8
```

### Deploy and Verify with Ganache

```bash
brownie console
```

In the console use the following steps.

```python
from scripts.deploy_fire import help
help()
```

The help command then shows an example session.
```python
from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help

(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instance, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=True)

verify_deploy(d, usdc, product)
```

### Deploy to differnt Network with existing Instance

As an example use the Ganache chain that runs in the background of this devcontainer setup.

```bash
brownie console --network=ganache
```

With an existing instance set parameter `deploy_all=False`.
In this case the file `gif_instance_address.txt` needs to exist and contain the addresses of the instance registry.
The file should be automatically created during the devconainer setup procedure of this repository.

```python
from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help

(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instance, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=False)

verify_deploy(d, usdc, product)
```
