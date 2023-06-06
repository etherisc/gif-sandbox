#!/bin/bash
brownie networks add Local ganache host=http://ganache:7545 chainid=1234

.devcontainer/scripts/deploy-gif.sh 

echo '>>>> Compiling sandbox contracts ...'
echo "" > .env 
rm -rf build/ .hypothesis/
brownie compile --all 

if grep -q "usd1=" "/workspace/gif_instance_address.txt"; then
    echo ">>>> gif_instance_address.txt exists. No sandbox deployment"
    exit 0
fi

# echo "Deploying the sandbox contracts to ganache ..."
touch /workspace/.env
touch /home/vscode/.brownie/packages/etherisc/gif-contracts@b58fd27/.env
brownie console --network=ganache <<EOF
from scripts.deploy_fire import all_in_1, verify_deploy, create_bundle, create_policy, help
(customer, customer2, product, oracle, riskpool, riskpoolWallet, investor, usdc, instance, instanceService, instanceOperator, bundleId, processId, d) = all_in_1(deploy_all=False)
verify_deploy(d, usdc, product)
f = open("/workspace/gif_instance_address.txt", "a")
f.writelines("product=%s\n" % (product.address))
f.writelines("productId=%s\n" % (product.getId()))
f.writelines("riskpool=%s\n" % (riskpool.address))
f.writelines("riskpoolId=%s\n" % (riskpool.getId()))
f.writelines("oracle=%s\n" % (oracle.address))
f.writelines("oracleId=%s\n" % (oracle.getId()))
f.writelines("usdc=%s\n" % (usdc.address))
f.writelines("customer=%s\n" % (customer.address))
f.writelines("instance=%s\n" % (instance.address))
f.writelines("instanceService=%s\n" % (instanceService.address))
f.close()
EOF

