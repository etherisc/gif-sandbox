// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;

import "@etherisc/gif-interface/contracts/0.7/Oracle.sol";


contract HelloWorldOracle is Oracle {

    bytes1 public constant RESPONSE_CODE_KIND = "K";
    bytes1 public constant RESPONSE_CODE_NONE = "N";
    bytes1 public constant RESPONSE_CODE_RUDE = "R";

    uint256 private _requestCounter;

    event LogOracleRequest(uint256 requestId, bytes32 greeting);
    event LogOracleResponse(uint256 requestId, bytes data);

    constructor(
        address gifOracleService,
        address gifOracleOwnerService,
        bytes32 oracleTypeName,
        bytes32 oracleName
    )
        Oracle(gifOracleService, gifOracleOwnerService, oracleTypeName, oracleName)
    { }

    // TODO check with christoph if input should be bytes32, bytes32 instead of bytes
    // ie if abi.decode in function can be avoided 
    function request(uint256 requestId, bytes calldata input) 
        external 
        override 
        onlyQuery
    {
        (/* bytes32  policyId */, bytes32 greeting) = abi.decode(input, (bytes32, bytes32));
        emit LogOracleRequest(requestId, greeting);

        bytes1 greetingResponseCode = _obtainDummyResponse(greeting);

        _handleResponse(requestId, greetingResponseCode);
    }

    function _obtainDummyResponse(bytes32 /* greeting */) 
        internal
        returns (bytes1 greetingResponseCode)
    {
        uint256 reminder = _requestCounter % 6;

        if (reminder <= 2) {
            // 50% get a kind response to greeting
            greetingResponseCode = RESPONSE_CODE_KIND;
        } else if (reminder <= 4) {
            // 33.3% get no resonse
            greetingResponseCode = RESPONSE_CODE_NONE;
        } else {
            // 16.6% get a rude response
            greetingResponseCode = RESPONSE_CODE_RUDE;
        }

        _requestCounter += 1;
    }

    function _handleResponse(uint256 requestId, bytes1 greetingResponseCode) internal {
        bytes memory data = abi.encode(bytes1(greetingResponseCode));

        // trigger inherited oracle response handling
        _respond(requestId, data);

        emit LogOracleResponse(requestId, data);
    }
}