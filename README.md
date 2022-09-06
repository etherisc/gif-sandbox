# GIF Sandbox

This GIF sandbox repository has the aim to provide a hands-on introduction into working with decentralized insurance products based on Generalized Insurance Framework (GIF) created by Etherisc. 

This GIF sandbox setup walks you through 

* Setting up a local Ganache chain
* Deploying your own GIF instance to Ganache
* Starting an API server for the "Fire Insurance" sample product.

The API server provides a simple web UI in the browser.
The API servers is first used to deploy the "Fire Insurance" product to your local GIF instance.
The API server can then be used to create fire policies and interact with those fire policies.

The sandbox can be deployed in two ways:
  - as a Visual Studio Code Devcontainer (mostly automatic setup)
  - installing GIF and product by hand (mostly manual setup)

## Prerequisites

This readme is based on the following assumption 
* You are familiar with bash shell commands
* You are familiar with Docker 
* You are familiar with git
* Your installation includes bash, Docker and git

PLEASE NOTE: The shell commands below are written for a bash shell.
If you are working on a Windows box you may use WSL2, Git Bash on Windows or similar. 

Before you start to clone any repositories decide on a parent directory where you want to store the various repositories that are needed for the sandbox environment.

## Devcontainer based setup

The setup for the devcontainer works very similar to the description for our [development environment](https://github.com/etherisc/gif-sandbox/blob/master/docs/development_environment.md). 

The only difference being that you need to clone the [gif-sandbox repository](https://github.com/etherisc/gif-sandbox). From there on follow the description of the development environment in the devconainer. Just be a bit patient with the post-installation script as it will a complete GIF instance it might take some minutes to complete. 

Once the devcontainer has finished starting (the last log message you will see in the log is `Sandbox ready - GIF Registry address in gif_instance_address.txt`) you can get the address of the GIF instance from the file `gif_instance_address.txt`. Also running `brownie console --network=ganache` will give you a brownie console connected to the local Ganach chain that as the GIF instance deployed. Now you can continue below in the section _Deploy the "Fire Insurance" Product_. 

## Manual setup of GIF and product

In the example below this parent directory is called sandbox-root. 
For the steps further below we only rely on the existence of the environment variable `GIF_SANDBOX_ROOT`.
The actual name of the sandbox root directory does not matter.

```bash
mkdir sandbox-root
cd sandbox-root
export GIF_SANDBOX_ROOT=$PWD
```

### Create the Sandbox Setup

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

Build the Brownie docker image.

```bash
cd docker
docker build . -t brownie
cd $SANDBOX
```

### Start a Local Ganache Chain

As the brownie image contains an embedded [Ganache](https://trufflesuite.com/ganache/index.html) chain we can also use this image to create a Ganache container as shown below.

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

### Deploy GIF to Ganache

Start an interactive Brownie container.

```bash
cd $GIF
docker run -it --rm -v $PWD:/projects brownie
```

In the Brownie container compile all the GIF with all its dependencies.

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

PLEASE NOTE: Save this GIF registry address for later, you will need it to deploy example insurance projects.

### The "Fire Insurance" API Server

Open a new shell and change to your sandbox directory and start a Brownie container.

```bash
cd <your path>/sandbox-root/gif-sandbox
docker run -p 8000:8000 -it --rm -v $PWD:/projects brownie
```

In the Brownie container compile the example contracts and add ganache to the networks managed by Brownie.

```bash
brownie compile --all
brownie networks add Local ganache host=http://host.docker.internal:7545 chainid=1234
```

Start the "Fire Insurance" API sever.

```bash
uvicorn server.api:app --log-level info --host 0.0.0.0 --reload
```

In case the above command leads to error messages like 
`brownie.exceptions.ContractNotFound: No contract deployed at 0x...` 
this might caused by brownie book keeping of previous contracts that is probably not relevant in your situation.
In this case delete the files in directory `build/deployments/*` and try to start the API server again.

After the application startup has completed successfully open the OpenAPI UI in your web browser
[http://localhost:8000/docs](http://localhost:8000/docs).

## Deploy the "Fire Insurance" Product

Switch to the [POST Config endpoint](http://localhost:8000/docs#/Config/set_node_config_config_post) of the API server
Click **Try it out** and provide the GIF registry contract address and the mnemonic to setup the GIF sandbox accounts in the request body field (replace the comment with the registry address from your GIF instance).
Clicking on **Execute** in the UI will trigger the deployment of the "Fire Insurance" product to the GIF instance.

```json
{
  "registry_address": "<your GIF registry contract address>",
  "mnemonic": "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
}
```
After a successful deploy the product and oracle addresses of the fire insurance are shown in the response body field. PLEASE NOTE: You should save the product address for later.

```json
{
  "product_address": "0x2E2D10b41b7c8DDb995568A87185428d9A513ead",
  "oracle_address": "0x4D2D24899c0B115a1fce8637FCa610Fe02f1909e",
  "mnemonic": "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat",
  ...
}
```

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

A successful policy creation also triggers a corresponding oracle request that is shown at the [GET Requests](http://localhost:8000/docs#/Oracle/get_oracle_requests_requests_get) endpoint.
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

Use the [PUT Request](http://localhost:8000/docs#/Oracle/respond_to_oracle_request_requests__request_id__respond_put) endpoint to trigger a response to the oracle request.
Enter the request ID and the category of the fire observed.

* For `request_id` enter `<requestId corresponding to your policy>`
* For `fire_category` enter `M`

Send this request to the "Fire Oracle" by clicking on **Execute**.
You can now verify the updated balances of the fire contract and the customer account in the shell you used to deploy the GIF instance.

```bash
Wei(web3.eth.getBalance('<your product contract address>')).to('wei')
Wei(accounts[3].balance()).to('wei')
```

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
