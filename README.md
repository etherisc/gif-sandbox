# GIF Sandbox

## Prerequisites

This readme is based on the following assumption 
* You are familiar with bash shell commands
* You are familiar with Docker 
* You are familiar with git
* Your installation includes bash, Docker and git

PLEASE NOTE The shell commands below are written for a bash shell.
If you are working on a Windows box you may use WSL2, Git Bash on Windows or similar. 

Before you start to clone any repositories decide on a parent directory where you want to store the various repositories that are needed for the sandbox environment.

In the example below this parent directory is called sandbox-root. 
For the steps further below we only rely on the existence of the environment variable `GIF_SANDBOX_ROOT`
The actual name of the sandbox root directory does not matter.

```bash
mkdir sandbox-root
cd sandbox-root
export GIF_SANDBOX_ROOT=$PWD
```

## Create the Sandbox Setup

To create the sandbox setup start by cloning the GIF sandbox and contracts repositories and build a docker image for Brownie.

Clone the GIF sandbox repository.

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-sandbox.git
cd gif-sandbox
export SANDBOX=$PWD
```

Clone the GIF contracts repository.

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-contracts.git
cd gif-contracts
export GIF=$PWD
```

And in the same directory build the Brownie docker image

```bash
docker build . -t brownie
```

<!-- ### Clone the GIF Monitor Repository

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-monitor.git
cd gif-monitor
export GIF_MONITOR=$PWD
``` -->

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

The chosen setup deterministically creates addresses (and private keys) via a HD wallet with the mnemonic `"candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"`.
Port `7545` is chosen to avoid conflicts with any productive local ethereum client that typically run on port 8545.

To connect with Metamaks using the mnemonic as secret recovery phrase.
As network parameter use `http://localhost:7545` as RPC URL and `1234` as Chain ID.

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

Then, add the ganache chain to the networks available to Brownie (see Brownie [Network Managment](https://eth-brownie.readthedocs.io/en/stable/network-management.html) for details) and start a Brownie console that connects to this network.

```bash
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
brownie console --network ganache
```

A new GIF Instance can now be deployed in the Brownie console.
As Brownie recognizes the network and provides access to its accounts we can use `accounts[0]` as the owner of the GIF instance.
```bash
from scripts.instance import GifInstance

owner = accounts[0]
instance = GifInstance(owner)
```

Use the following command to print the registry address of the newly deployed GIF instance.
```bash
>>> instance.getRegistry().address
'0xF12b5dd4EAD5F743C6BaA640B0216200e89B60Da'
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

Inside the Brownie container compile the contracts, add the ganache chain and start a console attached to this chain.

```bash
brownie compile --all
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
brownie console --network ganache
```

Inside the Brownie console create the setup below.

```bash
owner = accounts[0]
oracleOwner = accounts[1]
productOwner = accounts[2]
registryAddress = '0xF12b5dd4EAD5F743C6BaA640B0216200e89B60Da'
```

IMPORTANT: Make sure that `registryAddress` matches with your GIF instance.

```bash
from scripts.instance import Instance
from scripts.helloworld import HelloWorld

instance = Instance(registryAddress, owner)
helloWorld = HelloWorld(oracleOwner, productOwner, instance)
```


And to deploy the "Fire" Insurance
```bash
from scripts.instance import Instance
from scripts.fire import Fire

owner = accounts[0]
oracleOwner = accounts[1]
productOwner = accounts[2]
customer = accounts[3]

registryAddress = '0xbbE595Df857805ab3734f15BE990f9A30CBB89F3'

instance = Instance(registryAddress, owner)
fire = Fire(oracleOwner, productOwner, instance)
```

Before any policy applications can be made you need to fund the "Fire" insurance product
```bash
risk_capital=1000000
fire.contract.deposit({'from':productOwner, 'amount':risk_capital})

premium=1000
tx = fire.contract.applyForPolicy('dog-house', {'from':customer, 'amount':premium})
tx.info()

small = bytes('S', 'ascii')[0]
medium = bytes('M', 'ascii')[0]
large = bytes('L', 'ascii')[0]

fire.contract.balance()

oracle_tx = fire.oracle.contract.respond(0, medium, {'from':oracleOwner})

fire.contract.balance()
oracle_tx.info()

tx_expire = fire.contract.expirePolicy(0xde16105e9976d153f6a79e2afa46c3df2a333d1e33493145ebdf4c388cd8fc59)
```


## Interact with the "Hello World" Product

To interact with the deployed "Hello World" product we can remain in the Brownie console and use the `helloWorld` object.

The creation of a new "Hello World" policy is shown below.
In the provided example a new policy is created for the `customer` account by calling smart contract method `applyForPolicy` and transferring 1.0 ETH as premium amount.

```bash
contract = helloWorld.contract
Wei(contract.balance()).to('ether')

customer = accounts[3]
premium = Wei("1.0 ether")
tx = contract.applyForPolicy({'from':customer, 'amount':premium})
Wei(contract.balance()).to('ether')

id = tx.return_value
```

The policy `id` is obtaines from the transaction return value and can be used to make a claim for the newly created policy.

The "Hello World" product insures a friendly reply to a greeting of the insured.
Missing or rude replies are considered loss events by the "Hello World" and result in a payout.

Let's start with `hello` as a greeting.

```bash
tx = contract.greet(policyId, 'hello', {'from': customer})
Wei(contract.balance()).to('ether')
tx.info()
```

The HelloWorld oracle provides the outcome of a friendly reply (in fact any greeting starting with an 'h' will lead to a friendly reply with our oracle).
This is why the contract balance remains the same and we do not get a payout.

Single payouts (payout = premium) can be forced by empty greetings '' and triple payouts by greetings that start with a letter other than 'h'.
Please note that triple payouts imply that the helloworld contract does have sufficient funding for such a payout.

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

