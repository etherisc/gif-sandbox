// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.2;

import "@etherisc/gif-interface/contracts/components/Oracle.sol";

contract FireOracle is Oracle {

    event LogFireOracleRequest(
        uint256 requestId, 
        string objectName
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
        // decode oracle input data
        (string memory objectName) = abi.decode(input, (string));
        emit LogFireOracleRequest(requestId, objectName);
    }

    function respond(uint256 requestId, bytes1 fireCategory) 
        external
    {
        // input validation
        require(
            (fireCategory == 'S') || 
            (fireCategory == 'M') || 
            (fireCategory == 'L'), 
            "fire category not in (S,M,L)");

        // encode oracle output (response) data and
        // trigger inherited response handling
        bytes memory output = abi.encode(fireCategory);
        _respond(requestId, output);
    }

    function cancel(uint256 requestId)
        external override
    {
        // TODO mid/low priority
        // cancelChainlinkRequest(_requestId, _payment, _callbackFunctionId, _expiration);
    }
}