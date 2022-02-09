const log = console
const truffleConfig = require('../truffle-config')

const IRegistryFacade = artifacts.require('IRegistryFacade.sol')
const IOperatorServiceFacade = artifacts.require('IOperatorServiceFacade.sol')

const HelloWorldInsurance = artifacts.require('HelloWorldInsurance.sol')

const productServiceB32 = web3.utils.asciiToHex('ProductService')
const operatorServiceB32 = web3.utils.asciiToHex('InstanceOperatorService')

module.exports = async (deployer, network /* , accounts */) => {

  // TODO oracleId, productId should not be a constants
  // rather, should be queryable via deployed contracts
  const { gifRegistry, productName, productId, oracleTypeName, oracleId } = truffleConfig.networks[network]
  const registry = await IRegistryFacade.at(gifRegistry)

  const gifProductService = await registry.getContract(productServiceB32)
  const gifOperatorService = await registry.getContract(operatorServiceB32)
  
  log.log(`Registry Address: ${gifRegistry}`)
  log.log(`ProductService Address: ${gifProductService}`)
  log.log(`InstanceOperatorService Address: ${gifOperatorService}`)

  const operatorService = await IOperatorServiceFacade.at(gifOperatorService)

  log.log(`Deploying HelloWorldInsurance: ${productName} ...`)
  await deployer.deploy(
    HelloWorldInsurance,
    gifProductService,
    web3.utils.asciiToHex(productName),
    web3.utils.asciiToHex(oracleTypeName),
    oracleId
  )

  const helloWorldInsurance = await HelloWorldInsurance.deployed()
  log.log(`Deployed HelloWorldInsurance ${productId} at ${helloWorldInsurance.address}`)  

  log.log(`Approve HelloWorldInsurance ${productId} ...`)
  await operatorService.approveProduct(productId)
}
