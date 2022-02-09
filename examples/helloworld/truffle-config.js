require('dotenv').config()
const HDWalletProvider = require('@truffle/hdwallet-provider');
const { settings } = require('./package')

const hdWalletConfig = {
  development: {
    mnemonic: process.env.DEV_MNEMONIC,
    providerOrUrl: process.env.DEV_HTTP_PROVIDER,
  },
}

module.exports = {

  networks: {
  
    migrations_directory: process.env.MIGRATIONS_DIRECTORY || './migrations',
    contracts_build_directory: process.env.CONTRACTS_BUILD_DIRECTORY || './build',
    
    development: {
      provider: () => new HDWalletProvider(hdWalletConfig.development),

      httpProvider: process.env.DEV_HTTP_PROVIDER,
      host: process.env.DEV_HOST,
      port: process.env.DEV_PORT,
      network_id: process.env.DEV_NETWORK_ID,

      gas: process.env.GAS,
      gasPrice: process.env.GASPRICE,
      websockets: process.env.WEBSOCKETS,
      skipDryRun: true,

      gifRegistry: process.env.DEV_GIF_REGISTRY,
      gifProductService: process.env.DEV_GIF_PRODUCT_SERVICE,

      oracleTypeName: process.env.ORACLE_TYPE_NAME,
      oracleName: process.env.ORACLE_NAME,
      oracleId: process.env.ORACLE_ID,
      
      productName: process.env.PRODUCT_NAME,
      productId: process.env.PRODUCT_ID,
    },
  },

  // Set default mocha options here, use special reporters etc.
  mocha: {
    // timeout: 100000
  },

  // Configure your compilers
  compilers: {
    solc: {
      version: settings.solc,
      settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
        evmVersion: 'istanbul',
      },
    },
  },
};
