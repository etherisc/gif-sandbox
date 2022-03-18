// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "@gif-interface/contracts/Oracle.sol";


contract HelloWorldOracle is Oracle {

    bytes1 public constant RESPONSE_CODE_KIND = "K";
    bytes1 public constant RESPONSE_CODE_NONE = "N";
    bytes1 public constant RESPONSE_CODE_RUDE = "R";

    uint256 private _requestCounter;

    event LogHelloWorldOracleRequestReceived(uint256 requestId, string greeting);
    event LogHelloWorldOracleResponseHandled(uint256 requestId, AnswerType answer);

    enum AnswerType {Kind, None, Rude}

    constructor(
        address gifOracleService,
        address gifOracleOwnerService,
        bytes32 oracleTypeName,
        bytes32 oracleName
    )
        Oracle(gifOracleService, gifOracleOwnerService, oracleTypeName, oracleName)
    { }

    function request(uint256 requestId, bytes calldata input) 
        external 
        override 
        onlyQuery
    {
        // decode oracle input data
        (string memory input_greeting) = abi.decode(input, (string));
        emit LogHelloWorldOracleRequestReceived(requestId, input_greeting);

        // calculate and encode oracle output (response) data
        AnswerType output_answer = _oracleBusinessLogic(input_greeting);
        bytes memory output = abi.encode(AnswerType(output_answer));

        // trigger inherited response handling
        _respond(requestId, output);
        emit LogHelloWorldOracleResponseHandled(requestId, output_answer);
    }

    // this is just a toy example
    // real oracle implementations will get the output from some 
    // off chain component providing the outcome of the business logic
    function _oracleBusinessLogic(string memory /* greeting */) 
        internal
        returns (AnswerType answer)
    {
        uint256 reminder = _requestCounter % 6;

        if (reminder <= 2) {
            // 50% get a kind response to greeting
            answer = AnswerType.Kind;
        } else if (reminder <= 4) {
            // 33.3% get no resonse
            answer = AnswerType.None;
        } else {
            // 16.6% get a rude response
            answer = AnswerType.Rude;
        }

        _requestCounter += 1;
    }

    function getAnswerCodeKind() public pure returns (bytes1 code) { return RESPONSE_CODE_KIND; }
    function getAnswerCodeNone() public pure returns (bytes1 code) { return RESPONSE_CODE_NONE; }
    function getAnswerCodeRude() public pure returns (bytes1 code) { return RESPONSE_CODE_RUDE; }
}