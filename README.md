![Build](https://github.com/etherisc/depeg-contracts/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![](https://dcbadge.vercel.app/api/server/cVsgakVG4R?style=flat)](https://discord.gg/Qb6ZjgE8)

# Fire Insurance Demo

This repository holds the smart contracts for a demo fire insurance.

## Setup Requirements

1. A running Docker installation
1. Developing with VS Code
1. Working with dev containers

Installing Docker on Windows is sometimes a struggle.
Recommended Approach: Follow the installation instructions for [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/).
Installing Docker on Linux or Mac should be straight forward.

## Interaction via Command Line

### Running Unit Tests

Start with compiling all contracts.
```bash
brownie compile --all
```

Before running the tests for the first time you will likely need to add an empty `.env` file before.

```bash
touch /home/vscode/.brownie/packages/etherisc/gif-contracts@b58fd27/.env
```

Now run the unit tests for the sandbox.
```bash
brownie test -n auto
```

This shoud result in output similar to the one provided below.
```bash
⬢ [Docker] ❯ brownie test -n auto
Brownie v1.19.3 - Python development framework for Ethereum

================================================================= test session starts =================================================================
platform linux -- Python 3.9.16, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /workspace
plugins: eth-brownie-1.19.3, forked-1.4.0, hypothesis-6.27.3, web3-5.31.3, xdist-1.34.0, anyio-3.6.2
gw0 [8] / gw1 [8] / gw2 [8] / gw3 [8] / gw4 [8] / gw5 [8] / gw6 [8] / gw7 [8]
........                                                                                                                                        [100%]
-- Docs: https://docs.pytest.org/en/stable/warnings.html
========================================================== 8 passed, 101 warnings in 44.52s ===========================================================
```

The important part is that all tests pass and no errors or failures are shown.
 
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
