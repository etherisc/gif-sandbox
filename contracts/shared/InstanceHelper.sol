// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "@gif-interface/contracts/IInstanceOperatorService.sol";
import "@gif-interface/contracts/IOracleOwnerService.sol";
import "@gif-interface/contracts/IOracleService.sol";
import "@gif-interface/contracts/IProductService.sol";
import "@gif-interface/contracts/IRegistryAccess.sol";

contract InstanceHelper {

    bytes32 public constant INSTANCE_OPERATOR_SERVICE = "InstanceOperatorService";
    bytes32 public constant ORACLE_OWNER_SERVICE = "OracleOwnerService";
    bytes32 public constant ORACLE_SERVICE = "OracleService";
    bytes32 public constant PRODUCT_SERVICE = "ProductService";

    IInstanceOperatorService private _operatorService;
    IOracleOwnerService private _oracleOwnerService;
    IOracleService private _oracleService;
    IProductService private _productService;
    IRegistryAccess private _registry;

    constructor(address registryAddress) {
        _registry = IRegistryAccess(registryAddress);
        _operatorService = IInstanceOperatorService(_registry.getContractFromRegistry(INSTANCE_OPERATOR_SERVICE));
        _oracleOwnerService = IOracleOwnerService(_registry.getContractFromRegistry(ORACLE_OWNER_SERVICE));
        _oracleService = IOracleService(_registry.getContractFromRegistry(ORACLE_SERVICE));
        _productService = IProductService(_registry.getContractFromRegistry(PRODUCT_SERVICE));
    }

    function oracles() external view returns (uint256) { return _operatorService.oracles(); }
    function products() external view returns (uint256) { return _operatorService.products(); }

    function getInstanceOperatorService() external view returns (IInstanceOperatorService) { return _operatorService; }
    function getOracleOwnerService() external view returns (IOracleOwnerService) { return _oracleOwnerService; }
    function getOracleService() external view returns (IOracleService) { return _oracleService; }
    function getProductService() external view returns (IProductService) { return _productService; }
    function getRegistry() external view returns (IRegistryAccess) { return _registry; }
}