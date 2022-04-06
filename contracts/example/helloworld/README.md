# "Hello World" Insurance Product

## Preparations

As described in the main README file of this repository start with walking through all steps until and including "Deploy GIF to Ganache"

## Manually Deploy "Hello World"

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

