const log = console
const truffleConfig = require('../truffle-config')

const IOracleOwnerService = artifacts.require('@etherisc/gif-interface/contracts/0.7/IOracleOwnerService.sol')

const IRegistryFacade = artifacts.require('IRegistryFacade.sol')
const IOperatorServiceFacade = artifacts.require('IOperatorServiceFacade.sol')

const oracleOwnerServiceB32 = web3.utils.asciiToHex('OracleOwnerService')
const operatorServiceB32 = web3.utils.asciiToHex('InstanceOperatorService')

// this type name needs to match with the name used to deploy the hello world oracle
const oracleInputFormat = '(bytes input)'
const oracleOutputFormat = '(bytes1 greetingResponseCode)'

module.exports = async (deployer, network /* , accounts */) => {

  const { gifRegistry, oracleTypeName } = truffleConfig.networks[network]
  const registry = await IRegistryFacade.at(gifRegistry)

  const gifOracleOwnerService = await registry.getContract(oracleOwnerServiceB32)
  const gifOperatorService = await registry.getContract(operatorServiceB32)
  
  log.log(`Registry Address: ${gifRegistry}`)
  log.log(`OracleOwnerService Address: ${gifOracleOwnerService}`)
  log.log(`InstanceOperatorService Address: ${gifOperatorService}`)

  const oracleOwnerService = await IOracleOwnerService.at(gifOracleOwnerService)
  const operatorService = await IOperatorServiceFacade.at(gifOperatorService)

  const oracleTypeNameB32 = web3.utils.asciiToHex(oracleTypeName)

  log.log(`Propose Oracle Type: ${oracleTypeName} ...`)
  await oracleOwnerService.proposeOracleType(
    oracleTypeNameB32, 
    oracleInputFormat,
    oracleOutputFormat
  )

  log.log(`Approve Oracle Type: ${oracleTypeName} ...`)
  await operatorService.approveOracleType(oracleTypeNameB32)
}
