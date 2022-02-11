// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;


interface IHelloWorldInsurance {

    // events
    event LogGreetingPolicyCreated(bytes32 policyId);
    event LogGreetingRequest(uint256 requestId, bytes32 policyId, bytes32 greeting);
    event LogGreetingCallback(uint256 requestId, bytes32 policyId, bytes response);
    event LogPayoutTransferred(bytes32 policyId, uint256 claimId, uint256 payoutId, uint256 amount);
    event LogPolicyExpired(bytes32 policyId);

    // functions
    function applyForPolicy() external payable returns (bytes32 policyId);
    function greet(bytes32 policyId, bytes32 greeting) external;
    function withdraw(uint256 amount) external;
}