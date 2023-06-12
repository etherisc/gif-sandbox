// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.2;

import "@etherisc/gif-interface/contracts/components/Oracle.sol";

contract FireOracle is Oracle {

    event LogFireOracleRequest(
        uint256 requestId, 
        string objectName
    );

    mapping(string /* objectName */ => uint256) private _requestIdMap;
    uint256 private _requestIds = 0;

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
        _requestIdMap[objectName] = requestId;
        _requestIds += 1;
        emit LogFireOracleRequest(requestId, objectName);
    }

    function requestId(string calldata objectName) external view returns (uint256) {
        return _requestIdMap[objectName];
    }

    function requestIds() external view returns (uint256) {
        return _requestIds;
    }

    function cancel(uint256 requestId) external override {
        // nothing to implement for this demo case
    }

    function respond(uint256 requestId, bytes1 fireCategory) 
        external
        onlyOwner
    {
        // input validation
        require(
            (fireCategory == "S") || 
            (fireCategory == "M") || 
            (fireCategory == "L"), 
            "fire category not in (S,M,L)");

        // encode oracle output (response) data and
        // trigger inherited response handling
        bytes memory output = abi.encode(fireCategory);
        _respond(requestId, output);
    }
}