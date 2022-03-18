# GIF Sandbox

## Prerequisites

This readme is based on the following assumption 
* You are familiar with bash shell commands
* You are familiar with Docker 
* You are familiar with git
* Your installation includes bash, Docker and git

PLEASE NOTE The shell commands below are written for a bash shell.
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

* GIF Contracts
* GIF Sandbox
<!-- * GIF Monitor -->


### Clone the GIF Contracts Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-contracts.git
cd gif-contracts
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
export SANDBOX=$PWD
```

## Build Docker Images

Use the commands below to build the ganache and truffle images

```bash
cd $GIF
docker build . -t brownie
```

<!-- And the following commands to build the GIF monitor

```bash
cd $GIF_MONITOR
cp $GIF_SANDBOX/docker/.env.development ./.env
cp $GIF_SANDBOX/docker/images/meteor/Dockerfile .
docker build . -t gif-monitor
``` -->


## Start a Local Ganache Chain

As the brownie image contains an embedded [Ganache](https://trufflesuite.com/ganache/index.html) chain we can also use this image to create Ganache container as shown below.

```bash
docker run -d -p 7545:7545 --name ganache brownie ganache-cli \
    --mnemonic "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat" \
    --chainId 1234 \
    --port 7545 \
    -h "0.0.0.0"

```

### Ganache Chain Setup Considerations
Port 7545 is chosen to avoid conflicts with any productive local ethereum client that typically run on port 8545.

The chosen setup deterministically creates addresses (and private keys) via a HD wallet with the mnemonic `"candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"`. For the creation of the individual accounts the HD path `m/44'/60'/0'/0/{account_index}` is used.

The local Ganache chain comes with 10 initial accounts that are preloaded with 100 ETH each

* accounts[0]: 0x627306090abaB3A6e1400e9345bC60c78a8BEf57
* accounts[1]: 0xf17f52151EbEF6C7334FAD080c5704D77216b732
* accounts[2]: 0xC5fdf4076b8F3A5357c5E395ab970B5B54098Fef
* ...

### Connect Metamask to Ganache Chain

A Metamask wallet can be connect to this local Ganache chain by adding a new network via Metamask "Settings", "Networks", "Add Network" and specifying its property values as shown below

* Network Name: `ganache` (just about any name will do)
* New RPC URL: `http://localhost:7545` (port number needs to match with docker/ganache "port" command line paramters above)
* Chain ID: `1234` (id needs to match with ganache commande line paramter "chainId" above)
* Currency Symbol: `ETH` (just about any symbol you like)

When the menmonic `"candy ..."` from above is used as wallet seed phrase with Metamask the wallet will display account `0x627306090abaB3A6e1400e9345bC60c78a8BEf57`

## Deploy GIF to Ganache Chain

Start an interactive Brownie container

```bash
cd $GIF
docker run -it --rm -v $PWD:/projects brownie
```

In the Brownie container compile all the GIF with all its dependencies

```bash
brownie compile --all
```

In the Brownie container add the ganache chain to the networks available to Brownie.
See Brownie [Network Managment](https://eth-brownie.readthedocs.io/en/stable/network-management.html) for details about brownie networks.

```bash
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
```

Start Brownie console that connects to the ganache chain.

```bash
brownie console --network ganache
```

Brownie recognizes the network and provides access to its accounts. 
We can use `accounts[0]` as the owner of the GIF instance to be deployed.
```bash
print('network {} is_connected {}'.format(network.show_active(), network.is_connected()))
print('\n'.join(['{} {:.4f} ETH'.format(acc.address, Wei(acc.balance()).to('ether')) for acc in accounts]))
owner = accounts[0]
```

An owner account may also be directly created from a seed phrase
```bash
owner = accounts.from_mnemonic('candy maple cake sugar pudding cream honey rich smooth crumble sweet treat')
```

A new GIF Instance can now be deployed in the Brownie console.
```bash
from scripts.instance import GifInstance
instance = GifInstance(owner)
```

Use the following command to print the registry address of the newly deployed GIF instance.
```bash
>>> instance.getRegistry().address
'0x78f417302dE7D49046688e4E39807e6ADdc47877'
```

Save/copy this GIF registry address, you will need it to deploy example insurance projects.
Note that the GIF registry address will likely be different in your case. 

Exit the Brownie console and container (the 2nd exit)

```bash
>>> exit()
exit
```

## Deploy the "Hello World" Insurance Product

Change to your sandbox directory and start a Brownie container

```bash
cd $SANDBOX
docker run -it --rm -v $PWD:/projects brownie
```

Inside the Brownie container compile all example insurance product contracts and dependencies

```bash
brownie compile --all
```

Add the local ganache chain with the deployed GIF instance to Brownie and start a console attached to this chain.

```bash
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
brownie console --network ganache
```

Inside the Brownie console create the setup below.

```bash
from scripts.util import getInstanceOperatorService
from scripts.util import getOracleOwnerService
from scripts.util import s2b32

owner = accounts[0]
oracleOwner = accounts[1]
productOwner = accounts[2]

registryAddress = '0x78f417302dE7D49046688e4E39807e6ADdc47877'
```
IMPORTANT: Before you continue, make sure to change the value of the variable registryAddress to the GIF registry address that corresponds to your GIF instance.

```bash
helper = InstanceHelper.deploy(registryAddress, {'from': owner})
ios = getInstanceOperatorService(helper)
oos = getOracleOwnerService(helper)
```

With the oracle owner service `oss` you can now propose new oracle type and approve it using the instance operator service `ios`

```bash
oracleTypeNameB32 = s2b32('HelloWorld.OracleType.{}'.format(helper.oracleTypes()))

oos.proposeOracleType(
    oracleTypeNameB32, 
    '(bytes input)', 
    '(bytes1 greetingResponseCode)', 
    {'from': oracleOwner})

ios.approveOracleType(oracleTypeNameB32, {'from': owner})
```

The next step is to deploy a new oracle contract.
After creation the instance operator service is used to approve the new oracle and assign it to the oracle type created in the previous step. 

```bash
oracleNameB32 = s2b32('HelloWorld.Oracle.{}'.format(helper.oracles()))

oracle = HelloWorldOracle.deploy(
    helper.getOracleService(),
    helper.getOracleOwnerService(),
    oracleTypeNameB32,
    oracleNameB32,
    {'from': oracleOwner})

ios.approveOracle(oracle.getId(), {'from': owner})
ios.assignOracleToOracleType(oracleTypeNameB32, oracle.getId(), {'from': owner})
```

The final step is to deploy the insurance product contract and its approval by the instance operator service.

```bash
productNameB32 = s2b32('HelloWorld.Product.{}'.format(helper.products()))

product = HelloWorldInsurance.deploy(
    helper.getProductService(),
    productNameB32,
    oracleTypeNameB32,
    oracle.getId(),
    {'from': productOwner})

ios.approveProduct(product.getId(), {'from': owner})
```

The object `product` can now be used to interact with the "Hello World" insurance product.

As the product contract is now deployed on the local Ganache chain the address `product.address` of the product contract is all we need to start creating policies and making claims.

```bash
>>> product.address
'0x86BA3Fd3151E769311b295AFc81D80329616194f'
```

## Interact with the "Hello World" Product

To interact with the deployed "Hello World" product we can remain in the Brownie console and use the `product` object.
Alternatively, we can create a new product object that points to the same product contract address as shown below.

```bash
from scripts.util import getHelloWorldProduct

customer = accounts[3]
helloWorld = getHelloWorldProduct('0x86BA3Fd3151E769311b295AFc81D80329616194f')
```

The creation of a policy with the payment of the corresponding insurance premium is shown below.

```bash
premium = Wei("1.0 ether")

policyTx = helloWorld.applyForPolicy({'from':customer, 'amount':premium})
policyId = policyTx.return_value
```

The policyId can be used to make a claim.

The "Hello World" product insures a friendly reply to a greeting of the insured.
Missing or rude replies are considered loss events by the "Hello World" and result in a payout.

```bash
greeting = 'hey'

greetingTx = helloWorld.greet(policyId, greeting, {'from': customer})
greetingTx.info()
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

