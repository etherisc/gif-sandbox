# GIF Sandbox

## Prerequisites

This readme is based on the following assumption 
* You are familiar with bash shell commands
* You are familiar with Docker 
* You are familiar with git
* Your installation includes bash, Docker and git

## Preparations

Before you start to clone any repositories decide on a parent directory where you want to store the various repositories that are needed for the sandbox environment.

In the example below this parent directory is called sandbox-root. 
For the steps further below we only rely on the existence of the environment variable `GIF_SANDBOX_ROOT`
The actual name of the sandbox root directory does not matter.

```bash
mkdir sandbox-root
cd sandbox-root
export GIF_SANDBOX_ROOT=$PWD
```

## Clone the Repositories

For the sandbox setup you first need to clone the following repositories

* GIF
* GIF Monitor
* GIF Sandbox


### Clone the GIF Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/GIF.git
cd GIF
export GIF=$PWD
```

### Clone the GIF Sandbox Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-sandbox.git
cd gif-sandbox
export GIF_SANDBOX=$PWD
```

## Build Docker Images

```bash
cd $GIF_SANDBOX
docker build ./docker/images/ganache -t ganache-gif
docker build ./docker/images/truffle -t truffle-gif
```

## Run Ganache

```bash
docker run -p 7545:8545 -d --name ganache-gif ganache-gif
```

Port 7545 is chosen to avoid conflicts with any productive local ethereum client that typically run on port 8545.

The chosen setup deterministically creates addresses (and private keys) via a HD wallet with the mnemonic `"candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"`. For the creation of the individual accounts the HD path `m/44'/60'/0'/0/{account_index}` is used.

### Accounts with 1000 ETH each

* accounts[0]: 0x627306090abaB3A6e1400e9345bC60c78a8BEf57
* accounts[1]: 0xf17f52151EbEF6C7334FAD080c5704D77216b732
* accounts[2]: 0xC5fdf4076b8F3A5357c5E395ab970B5B54098Fef

### Private Keys for Accounts

0. 0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3
1. 0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f
2. 0x0dbbe8e4ae425a6d2687f1a7e3ba17bc98c673636790f1b8ad91193c05875ef1

## Deploy a GIF Instance

Before compiling and deploying prepare and enter the truffle container as shown below.

```bash
cd $GIF_SANDBOX
cp ./docker/env/.env.development $GIF/gif-contracts/.env
docker run -it --rm -v $GIF/gif-contracts:/app truffle-gif bash
```

In the running truffle container compile and deploy a GIF instance as shown below.
File `resources.yml` can be used to configure which contracts should be compiled and deployed.

The `nano` editor may be used to modify the default set of contracts to compile and migration scripts for contract deployment.

```bash
nano resources.yml
```

Based on the content of `resources.yml` the command `gif-tools select-resources` is used to populate the folders `contracts` and `migrations` based on the available source files in folders `contracts-available` and `migrations-available`.

```bash
gif-tools select-resources
npm install dotenv --save
truffle compile --all
truffle migrate --reset
```
