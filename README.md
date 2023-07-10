![Build](https://github.com/etherisc/gif-sandbox/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![](https://dcbadge.vercel.app/api/server/cVsgakVG4R?style=flat)](https://discord.gg/Qb6ZjgE8)

# GIF-Sandbox And Fire Insurance Demo

This repository holds the smart contracts, helper scripts and documentation for a fire insurance product.

The fire insurance product is a simple example product that can be used to demonstrate the basic functionality of the GIF platform. 
It is a simple parametric insurance product that pays out an amount of USDC if a fire event is triggered by the oracle depending on the fire category.

Detailed setup and usage instructions for the sandbox can be found on the [Sandbox documenation page](https://docs.etherisc.com/sandbox/). 


## Build and test using foundry

Foundry is a new tool to build and test smart contracts. 
More documentation about foundry can be found in the foundry [https://book.getfoundry.sh/](Foundry book).

The project is configured to use foundry. 
All contracts in the `contracts` folder can be compiled using foundry as well as brownie (results are stored in `build_foundry`). 
Foundry tests are writte in solidy and can be found in the `tests_foundry` folder (they need to be separate from brownie based tests).
Dependencies are stored in the `lib` folder and are mapped in the `foundry.yaml` config file.

To compile the contracts using foundry, run the following command:

```bash
forge build
```

To run the foundry based tests, run the following command:

```bash
forge test
```

## Contributing

See the [contributing guide](./CONTRIBUTING.MD) for detailed instructions on how to get started with our project.

