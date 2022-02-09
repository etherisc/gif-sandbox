const log = console
const truffleConfig = require('../truffle-config')

const IRegistryFacade = artifacts.require('IRegistryFacade.sol')
const IOperatorServiceFacade = artifacts.require('IOperatorServiceFacade.sol')

const HelloWorldOracle = artifacts.require('HelloWorldOracle.sol')

const oracleServiceB32 = web3.utils.asciiToHex('OracleService')
const oracleOwnerServiceB32 = web3.utils.asciiToHex('OracleOwnerService')
const operatorServiceB32 = web3.utils.asciiToHex('InstanceOperatorService')

module.exports = async (deployer, network /* , accounts */) => {

// TODO oracleId should not be a constant
// rather, should be queryable via deployed oracle contract
const { gifRegistry, oracleTypeName, oracleName, oracleId } = truffleConfig.networks[network]
  const registry = await IRegistryFacade.at(gifRegistry)

  const gifOracleService = await registry.getContract(oracleServiceB32)
  const gifOracleOwnerService = await registry.getContract(oracleOwnerServiceB32)
  const gifOperatorService = await registry.getContract(operatorServiceB32)
  
  log.log(`Registry Address: ${gifRegistry}`)
  log.log(`OracleService Address: ${gifOracleService}`)
  log.log(`OracleOwnerService Address: ${gifOracleOwnerService}`)
  log.log(`InstanceOperatorService Address: ${gifOperatorService}`)

  const operatorService = await IOperatorServiceFacade.at(gifOperatorService)

  const oracleTypeNameB32 = web3.utils.asciiToHex(oracleTypeName)
  const oracleNameB32 = web3.utils.asciiToHex(oracleName)
  log.log(`Deploying HelloWorldOracle: ${oracleName} ...`)
  
  oracleTypeName, oracleName
  await deployer.deploy(
    HelloWorldOracle,
    gifOracleService,
    gifOracleOwnerService,
    oracleTypeNameB32,
    oracleNameB32
  )

  const helloWorldOracle = await HelloWorldOracle.deployed()
  log.log(`Deployed HelloWorldOracle ${oracleId} at ${helloWorldOracle.address}`)

  log.log(`Approve HelloWorldOracle: ${oracleId} ...`)
  await operatorService.approveOracle(oracleId)

  log.log(`Assign to HelloWorldOracle ${oracleId} to oracle type ${oracleTypeName} ...`)
  await operatorService.assignOracleToOracleType(
    oracleTypeNameB32, 
    oracleId)
}
