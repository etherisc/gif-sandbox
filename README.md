![Build](https://github.com/etherisc/gif-sandbox/actions/workflows/build.yml/badge.svg)
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
Installing Docker on [Linux](https://docs.docker.com/desktop/install/linux-install/) or [Mac](https://docs.docker.com/desktop/install/mac-install/) should be straight forward.

When you have installed docker, check out the code, open it in VS Code and start the devcontainer (either wait for the pop to build the devcontainer or open the command list (F1) and select the command _Dev Containers: Rebuild and reopen in container_). Once the devcontainer is up and running and has finished compiling the contracts, you can start working with the code.

If you cannot run the vscode devcontainer, then see below in chapter _Run brownie container outside of vscode devcontainer_ for instructions how to run the brownie container manually. When the container is started, continue with the instructions in chapter _Interaction via Command Line_.

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

This will deploy a new GIF instance as well as the fire insurance product and verify the installation. 

### Deploy to a different network containing a pre-installed GIF instance

As an example use the Ganache chain that runs in a separate container (`ganache`) of this devcontainer setup.

```bash
brownie console --network=ganache
```

With an existing instance set parameter `deploy_all=False`.
In this case the file `gif_instance_address.txt` needs to exist and contain the addresses of the instance registry
The file should be automatically created during the devconainer setup procedure of this repository.

```python
from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help

(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instance, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=False)

verify_deploy(d, usdc, product)
```

### Interacting with the fire insurance product


```python
# Create a new policy for a house with a value of 1 million USD.
policy = product.applyForPolicy('The big house', 1000000 * 10 ** 6, {'from': accounts[9]})

# Retrieve the `processId` of the new policy
processId = policy.events['LogApplicationCreated'][0]['processId']

# Fetch the state of the applicaton (if [state == 2](https://github.com/etherisc/gif-interface/blob/develop/contracts/modules/IPolicy.sol#L58) -> policy is underwritten)
instanceService.getApplication(processId).dict()

# Fetch the state of the policy (if [state == 0](https://github.com/etherisc/gif-interface/blob/develop/contracts/modules/IPolicy.sol#L59) -> policy is active)
instanceService.getPolicy(processId).dict()
```


## Run brownie container outside of vscode devcontainer

Build the brownie container 

```bash
docker build -t gif-sandbox-brownie -f Dockerfile.brownie-container .
```

Run the brownie container

```bash
docker run -v .:/sandbox --name gif-sandbox-brownie gif-sandbox-brownie
```

Start an interactive shell in the brownie container to execute commands

```bash
docker exec -it gif-sandbox-brownie bash
```
