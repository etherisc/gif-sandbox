// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.2;

import "@etherisc/gif-interface/contracts/components/Oracle.sol";

contract CoorestOracle is Oracle {

    event LogCoorestOracleRequest(
        uint256 requestId, 
        bytes input
    );

    constructor(
        bytes32 oracleName,
        address registry
    )
        Oracle(oracleName, registry)
    { }

    function request(uint256 requestId, bytes calldata input) 
        external 
        override 
        onlyQuery
    {
        emit LogCoorestOracleRequest(requestId, input);
    }

    function respond(uint256 requestId, bytes memory output) 
        external
    {
        _respond(requestId, output);
    }

    function cancel(uint256 requestId) external override {
        // nothing to implement for this demo case
    }
}