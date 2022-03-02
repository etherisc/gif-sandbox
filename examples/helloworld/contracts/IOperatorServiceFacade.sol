// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.12;


interface IOperatorServiceFacade {
    
    function approveOracleType(bytes32 _oracleTypeName) external;
    function approveOracle(uint256 _oracleId) external;
    function assignOracleToOracleType(
        bytes32 _oracleTypeName,
        uint256 _oracleId
    ) external;

    function approveProduct(uint256 _productId) external;
}
