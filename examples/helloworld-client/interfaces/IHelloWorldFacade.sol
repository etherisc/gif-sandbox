// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;


interface IHelloWorldFacade {

    // helloworld product events
    event LogHelloWorldPolicyCreated(bytes32 policyId);
    event LogHelloWorldGreetingReceived(bytes32 policyId, string greeting);
    event LogHelloWorldGreetingCompleted(uint256 requestId, bytes32 policyId, string greeting);
    event LogHelloWorldPayoutExecuted(bytes32 policyId, uint256 claimId, uint256 payoutId, uint256 amount);
    event LogHelloWorldCallbackCompleted(uint256 requestId, bytes32 policyId, bytes response);
    
    // helloworld product functions
    function applyForPolicy() external payable returns (bytes32 policyId);
    function greet(bytes32 policyId, string calldata greeting) external;
    function withdraw(uint256 amount) external;
}