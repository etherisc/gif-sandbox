# GIF Sandbox

## Prerequisites

This readme is based on the following assumption 
* You are familiar with bash shell commands
* You are familiar with Docker 
* You are familiar with git
* Your installation includes bash, Docker and git

:warning: The shell commands below are written for a bash shell.
If you are working on a Windows box you may use WSL2, Git Bash on Windows or similar. 

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
* GIF Sandbox
<!-- * GIF Monitor -->


### Clone the GIF Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/GIF.git
cd GIF
export GIF=$PWD
```

<!-- ### Clone the GIF Monitor Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-monitor.git
cd gif-monitor
export GIF_MONITOR=$PWD
``` -->

### Clone the GIF Sandbox Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-sandbox.git
cd gif-sandbox
export GIF_SANDBOX=$PWD
```

## Build Docker Images

Use the commands below to build the ganache and truffle images

```bash
cd $GIF_SANDBOX
docker build ./docker/images/ganache -t gif-ganache
docker build ./docker/images/truffle -t gif-truffle
docker build ./docker/images/brownie -t gif-brownie
```

<!-- And the following commands to build the GIF monitor

```bash
cd $GIF_MONITOR
cp $GIF_SANDBOX/docker/.env.development ./.env
cp $GIF_SANDBOX/docker/images/meteor/Dockerfile .
docker build . -t gif-monitor
``` -->

## Run Ganache

```bash
docker run -p 7545:8545 -d --name ganache gif-ganache
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
cp ./docker/.env.development $GIF/gif-contracts/.env
cp ./docker/resources.yml.development $GIF/gif-contracts/resources.yml
docker run -it --rm -v $GIF/gif-contracts:/app gif-truffle bash
```

In the running truffle container compile and deploy a GIF instance as explained below.

```bash
gif-tools select-resources
truffle compile --all
truffle migrate --reset
```

File `resources.yml` is used by `gif-tools select-resources` to populate the folders `contracts` and `migrations` from the files in folders `contracts-available` and `migrations-available`.
The truffel commands then work with the files in the folders `contracts` and `migrations`

`truffle migrate` will update deployment meta data in the `./build/*.json` files of the deployed contracts.

```bash
grep '"address":' build/*json
```
Use tha command above to extract the addresses of the deployed GIF contracts.
The output of the grep command should then look similar to the example below.

```bash
...
build/Query.json: "address": "0xB529f14AA8096f943177c09Ca294Ad66d2E08b1f",
build/RegistryController.json: "address": "0x345cA3e014Aaf5dcA488057592ee47305D9B3e10",
build/Registry.json: "address": "0xf25186B5081Ff5cE73482AD761DB0eB0d25abfBF",
```

From the output shown above you need to look for the contract address shown.
As a result the registry address in the example above is `0xf25186B5081Ff5cE73482AD761DB0eB0d25abfBF`


## Deploy the "Hello World" Insurance Product

Ensure that the DEV_GIF_REGISTRY variable in the dotenv file contains the right GIF registry address of the GIF instance where you want to deploy the "Hello World" insurance product.

```bash
cd $GIF_SANDBOX
nano ./docker/.env.development 
```
For the example GIF deploy above the relevant line in file should read

```
DEV_GIF_REGISTRY="0xf25186B5081Ff5cE73482AD761DB0eB0d25abfBF"
```

Now, create a truffle container.

```bash
cp ./docker/.env.development $GIF_SANDBOX/examples/helloworld/.env
docker run -it --rm -v $GIF_SANDBOX/examples/helloworld:/app gif-truffle bash
```

Inside the container install npm dependencies, compile the "Hello World" contract and deploy to the local ganache

```bash
npm install
truffle compile --all
truffle migrate --reset
```

The "Hello World" product contract address may be obtaines from the output of the `truffle migrate` command or the  `HelloWorldInsurance.json` file.

```bash
grep '"address":' build/contracts/HelloWorldInsurance.json
```

Which produces an output similar to the one shown below.

```bash
"address": "0x9eFec315E368e8812025B85b399a69513Cd0e716",
```

We will need this "Hello World" contract address `0x9eFec315E368e8812025B85b399a69513Cd0e716` to interact with the "Hello World" product contract in the section below.


## Interact with the "Hello World" Insurance

For the interaction with the "Hello World" Insurance product the python script `check_helloworld_client.py` is used that relies on the [Brownie](https://eth-brownie.readthedocs.io/en/stable/) framework.

For the procedure below the following files in directory `/examples/helloworld-client` are important.

* Python client script: `./scripts/check_helloworld_client.py`
* "Hello World" Facade interface: `./interfaces/IHelloWorldFacade.sol`
* Event definitions:  `./interfaces/IEventFacade.sol`

The solidity files have zero external dependencies and are used by Brownie to create ABI files to interact with the on-chain part of the "Hello World" insurance contract.
These ABI files are created by the command `brownie compile --all` in sub-folder `./build/interfaces` (see below).

Make sure to adapt the constant `HELLOWORLD_CONTRACT_ADDRESS` in the Python script to the actual address of the deployed "Hello World" product contract.

Create a Brownie container

```bash
cd $GIF_SANDBOX
docker run -it --rm -v $PWD/examples/helloworld-client:/projects brownie
```

Inside the brownie container make brownie aware of our local gif-ganache chain.

```bash
brownie networks add Ethereum gif-ganache host=http://host.docker.internal:7545 chainid=1234
```

Compile the solidity facade interfaces and run the interaction script file.

```bash
brownie compile --all
brownie run check_helloworld_client --network=gif-ganache
```

A successful run of the script should the produce output similar to the one shown below.

```bash
Brownie v1.17.1 - Python development framework for Ethereum

ProjectsProject is the active project.

Running 'scripts/check_helloworld_client.py::main'...
current network: gif-ganache
helloworld contract address: 0x774DDa3beEf9650473549Be4EE7054a2ef5B0140
customer account address: 0xf17f52151EbEF6C7334FAD080c5704D77216b732

creating hello_world policy ...
Transaction sent: 0x1e0439df6beb0d72d27c99dba1aef9595a955d14c22fd9cac664b362c8567e98
  Gas price: 20.0 gwei   Gas limit: 590063   Nonce: 315
  IHelloWorldFacade.applyForPolicy confirmed   Block: 516   Gas used: 521666 (88.41%)

hello_world.applyForPolicy()
    policyId 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
hello_world.applyForPolicy() tx events
event[0] LogNewMetadata
    productId: 12
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    state: 0
event[1] LogNewApplication
    productId: 12
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
event[2] LogApplicationStateChanged
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    state: 2
event[3] LogNewPolicy
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
event[4] LogHelloWorldPolicyCreated
    policyId: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841

creating greeting claim ...
Transaction sent: 0xa8efc74d0594b7b76944f740100c44c5d3297526965ca5beb7e72215f23f29ac
  Gas price: 20.0 gwei   Gas limit: 584315   Nonce: 316
  IHelloWorldFacade.greet confirmed   Block: 517   Gas used: 493725 (84.50%)

hello_world.greet() tx events
event[0] LogHelloWorldGreetingReceived
    policyId: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    greeting: hey
event[1] LogHelloWorldOracleRequestReceived
    requestId: 91
    greeting: hey
event[2] LogPolicyStateChanged
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    state: 1
event[3] LogHelloWorldCallbackCompleted
    requestId: 91
    policyId: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    response: 0x0000000000000000000000000000000000000000000000000000000000000000
event[4] LogOracleResponded
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    requestId: 91
    responder: 0xE843CDE33060bf9CB11723934EAD6a3DE410DdEE
    status: True
event[5] LogHelloWorldOracleResponseHandled
    requestId: 91
    answer: 0
event[6] LogOracleRequested
    bpKey: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    requestId: 91
    responsibleOracleId: 12
event[7] LogHelloWorldGreetingCompleted
    requestId: 91
    policyId: 0x68a6e215fe86df103ce4f26d1e13c2f1626e68a7b76e3d747083a830d4498841
    greeting: hey
```

<!-- ## Random Stuff regarding "Hello World" insurance

TODOs

* make usage of truffle and brownie container more consistent

official style guides https://docs.soliditylang.org/en/latest/style-guide.html
in addition: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/GUIDELINES.md


## Run the GIF Monitor

Start the GIF monitor as shown below

```bash
docker run -p 8081:3000 -d --name gif-monitor gif-monitor
```

Starting up the GIF monitor takes a while.
To monitor the startup progress you can use.

```bash
docker logs -f gif-monitor

# the following output indicates that startup has completed
=> Started your app.
=> App running at: http://localhost:3000/
```

After startup open the GIF monitor application in the browser `http://localhost:8081`
 -->

