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

To create the sandbox setup start by cloning the GIF contracts and GIF sandbox repositories and build the Brownie docker image.

Clone the GIF contracts repository.

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-contracts.git
cd gif-contracts
export GIF=$PWD
```

Clone the GIF sandbox repository.

```bash
cd $GIF_SANDBOX_ROOT
git clone https://github.com/etherisc/gif-sandbox.git
cd gif-sandbox
export SANDBOX=$PWD
```

The next step is to build the Brownie docker image in the  directory of the GIF sandbox repository

```bash
docker build . -t brownie
```

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

## Deploy GIF to Ganache

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
instance = GifInstance(accounts[0])
```

Use the following command to print the registry address of your newly deployed GIF instance.
```bash
instance.getRegistry().address
```

PLEASE NOTE save/copy this GIF registry address, you will need it to deploy example insurance projects.

## The "Fire Insurance" API Server

Open a new shell and change to your sandbox directory and start a Brownie container

```bash
docker run -p 8000:8000 -it --rm -v $PWD:/projects brownie
```

In the Brownie container compile the example contracts and add 'ganache' to the networks managed by Brownie.

```bash
brownie compile --all
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
```

Start the "Fire Insurance" API sever.

```bash
uvicorn server.api:app --log-level info --host 0.0.0.0 --reload
```

After the application startup has completed open the OpenAPI UI in your web browser
[http://localhost:8000/docs](http://localhost:8000/docs)

### Deploy the "Fire Insurance" Product
Switch to the [POST Config endpoint](http://localhost:8000/docs#/Config/set_node_config_config_post) of the API server
Click **Try it out** and provide the GIF registry contract address and the mnemonic to setup the GIF sandbox accounts in the request body field (replace the comment with the registry address from your GIF instance).
Clicking on **Execute** in the UI will trigger the deployment of the "Fire Insurance" product to the GIF instance.

```json
{
  "registry_address": "<your GIF registry contract address>",
  "mnemonic": "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
}
```
After a successful deploy the product and oracle addresses of the fire insurance are shown in the response body field.

Before creating any policies check the balances of the product contract and the customer account in the shell you used to deploy the GIF instance.

```bash
Wei(web3.eth.getBalance('<your product contract address>')).to('wei')
Wei(accounts[3].balance()).to('wei')
```

### Create a new Policy
You can now create a new insurance policy using the [POST Policy](http://localhost:8000/docs#/Policy/apply_for_fire_policy_policies_post) endpoint.
Enter the name of the object to be insured and provide some policy amount.

* For `object_name` enter `My House`
* For `premium` enter `1000`

To create the policy with these values click on **Execute**.
You can now check the updated balances of the customer account (which should now have decreased by 1000 wei) and the product address (which should have increased by the same amount).

A successful policy creation also triggers a corresponding oracle request that is shown at the [GET Requests](http://localhost:8000/docs#/Oracle%20Request/get_oracle_requests_requests_get) endpoint.
An example output is shown below.

```json
[
  {
    "log_id": "(308,0,4)",
    "address": "0x83DcE984E34cfcFcA1b8572fde0E5dED714C7725",
    "event": "LogFireOracleRequest",
    "args": {
      "requestId": 17,
      "objectName": "My House"
    },
    "open": true,
    "fire_category": null
  }
]
```

The API server obtained this information from a corresponding log event that has been emitted by the fire oracle contract.

### Trigger a "Fire" Claim
Let us assume that we observe a medium sized fire for the object of the policy you just created.

Use the [PUT Request](http://localhost:8000/docs#/Oracle%20Request/respond_to_oracle_request_requests__request_id__respond_put) endpoint to trigger a response to the oracle request.
Enter the request ID and the category of the fire observed.

* For `request_id` enter `<requestId corresponding to your poilicy>`
* For `fire_category` enter `M`

Send this response to the "Fire Oracle" by clicking on **Execute**.
You can now verify the updated balances of the fire contract and the customer account.

To get a more detailed insight into the inner working of the product contract check the information available from the Ganache chain.
In the Brownie console that you used to deploy the GIF instance using `tx.info()` as shown below.

```bash
tx = chain.get_transaction('<last transaction hash from the API server command line output>')
tx.info()
```

A sample output of `tx.info()` is provided below.
```bash
Transaction was Mined
---------------------
Tx Hash: ...

Events In This Transaction
--------------------------
├── Policy (0x75c35C980C0d37ef46DF04d31A140b65503c0eEd)
│   ├── LogNewClaim
│   │   ├── bpKey: 0xa3ec67312c4b3883e111dda92cbd798368335f9210e95bfe84f9ce058a2287b8
│   │   ├── claimId: 0
│   │   └── state: 0
│   ├── LogClaimStateChanged
│   │   ├── bpKey: 0xa3ec67312c4b3883e111dda92cbd798368335f9210e95bfe84f9ce058a2287b8
│   │   ├── claimId: 0
│   │   └── state: 1
│   └── LogNewPayout
│       ├── bpKey: 0xa3ec67312c4b3883e111dda92cbd798368335f9210e95bfe84f9ce058a2287b8
│       ├── claimId: 0
│       ├── payoutId: 0
│       └── state: 0
...
│
├── Policy (0x75c35C980C0d37ef46DF04d31A140b65503c0eEd)
│   └── LogPayoutCompleted
│       ├── bpKey: 0xa3ec67312c4b3883e111dda92cbd798368335f9210e95bfe84f9ce058a2287b8
│       ├── payoutId: 0
│       └── state: 1
...
│
└── Query (0x38cF23C52Bb4B13F051Aec09580a2dE845a7FA35)
    └── LogOracleResponded
        ├── bpKey: 0xa3ec67312c4b3883e111dda92cbd798368335f9210e95bfe84f9ce058a2287b8
        ├── requestId: 18
        ├── responder: 0x83DcE984E34cfcFcA1b8572fde0E5dED714C7725
        └── status: True
```


## Manually Deploy the "Hello World" Insurance Product

Open a new shell and change to your sandbox directory and start a Brownie container

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

fire.contract.address
fire.oracle.contract.address
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

