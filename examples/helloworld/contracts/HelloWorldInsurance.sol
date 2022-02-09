// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;

import "@etherisc/gif-interface/contracts/0.7/Product.sol";


contract HelloWorldInsurance is Product {

    bytes32 public constant VERSION = "0.0.1";
    bytes32 public constant POLICY_FLOW = "PolicyFlowDefault";

    uint256 public constant MIN_PREMIUM = 100 * 10**16;
    uint256 public constant MAX_PREMIUM = 1500 * 10**16;

    uint256 public constant PAYOUT_FACTOR_RUDE_RESPONSE = 3;
    uint256 public constant PAYOUT_FACTOR_NO_RESPONSE = 1;
    uint256 public constant PAYOUT_FACTOR_KIND_RESPONSE = 0;

    uint16 public constant MAX_LENGTH_GREETING = 20;    
    string public constant CALLBACK_METHOD_NAME = "greetingCallback";

    uint256 public uniqueIndex;
    bytes32 public greetingsOracleType;
    uint256 public greetingsOracleId;

    mapping(bytes32 => address) public policyIdToAddress;
    mapping(address => bytes32[]) public addressToPolicyIds;

    event LogGreetingRequest(uint256 requestId, bytes32 policyId, bytes32 greeting);
    event LogGreetingCallback(uint256 requestId, bytes32 policyId, bytes response);

    event LogPayoutTransferred(bytes32 policyId, uint256 claimId, uint256 payoutId, uint256 amount);
    event LogPolicyExpired(bytes32 policyId);

    constructor(
        address gifProductService,
        bytes32 productName,
        bytes32 oracleType,
        uint256 oracleId
    )
        Product(gifProductService, productName, POLICY_FLOW)
    {
        greetingsOracleType = oracleType;
        greetingsOracleId = oracleId;
    }

    function applyForPolicy() external payable returns (bytes32 policyId) {

        address payable policyHolder = msg.sender;
        uint256 premium = _getValue();

        // Create new ID for this policy
        policyId = _uniqueId(policyHolder);

        // Validate input parameters
        require(premium >= MIN_PREMIUM, "ERROR:HWI-001:INVALID_PREMIUM");
        require(premium <= MAX_PREMIUM, "ERROR:HWI-002:INVALID_PREMIUM");

        // Create and underwrite new application
        _newApplication(policyId, abi.encode(premium, policyHolder));
        _underwrite(policyId);

        // Book keeping to simplify lookup
        policyIdToAddress[policyId] = policyHolder;
        addressToPolicyIds[policyHolder].push(policyId);
    }

    function greet(bytes32 policyId, bytes32 greeting) external {

        // Validate input parameters
        require(policyIdToAddress[policyId] == msg.sender, "ERROR:HWI-003:INVALID_POLICY_OR_HOLDER");
        require(greeting.length <= MAX_LENGTH_GREETING, "ERROR:HWI-004:GREETING_TOO_LONG");

        // request response to greeting via oracle call
        _requestOracleResponse(policyId, greeting);
    }

    function greetingCallback(uint256 requestId, bytes32 policyId, bytes calldata response)
        external
        onlyOracle
    {
        emit LogGreetingCallback(requestId, policyId, response);

        // get policy data for oracle response
        (uint256 premium, address payable policyHolder) = abi.decode(
            _getApplicationData(policyId), (uint256, address));

        // get oracle response data
        (bytes1 greetingResponseCode) = abi.decode(response, (bytes1));

        // claim handling based on reponse to greeting provided by oracle 
        _handleClaim(policyId, policyHolder, premium, greetingResponseCode);
        
        // policy only covers a single greeting/response pair
        // policy can therefore be expired
        _expire(policyId);

        emit LogPolicyExpired(policyId);
    }

    function withdraw(uint256 amount) public onlyOwner {
        require(amount <= address(this).balance);

        address payable receiver;
        receiver = payable(owner());
        receiver.transfer(amount);
    }

    function _getValue() internal returns(uint256 premium) { premium = msg.value; }

    function _uniqueId(address senderAddress) internal returns (bytes32 uniqueId) {
        uniqueIndex += 1;
        return keccak256(abi.encode(senderAddress, productId, uniqueIndex));
    }

    function _requestOracleResponse(bytes32 policyId, bytes32 greeting) internal {
        uint256 requestId = _request(
            policyId,
            abi.encode(greeting),
            CALLBACK_METHOD_NAME,
            greetingsOracleType,
            greetingsOracleId
        );

        emit LogGreetingRequest(requestId, policyId, greeting);
    }

    function _handleClaim(
        bytes32 policyId, 
        address payable policyHolder, 
        uint256 premium, 
        bytes1 greetingResponseCode
    ) 
        internal 
    {
        uint256 payoutAmount = _calculatePayoutAmount(premium, greetingResponseCode);

        // no claims handling for payouts == 0
        if (payoutAmount > 0) {
            uint256 claimId = _newClaim(policyId, abi.encode(payoutAmount));
            uint256 payoutId = _confirmClaim(policyId, claimId, abi.encode(payoutAmount));

            _payout(policyId, payoutId, true, abi.encode(payoutAmount));

            // actual transfer of funds for payout of claim
            policyHolder.transfer(payoutAmount);

            emit LogPayoutTransferred(policyId, claimId, payoutId, payoutAmount);
        }
    }

    function _calculatePayoutAmount(uint256 premium, bytes1 greetingResponseCode) 
        internal 
        pure 
        returns(uint256 payoutAmount) 
    {
        if (greetingResponseCode == "R") { // payout amount for rude response
            payoutAmount = PAYOUT_FACTOR_RUDE_RESPONSE * premium;
        } else if (greetingResponseCode == "N") { // for no response at all
            payoutAmount = PAYOUT_FACTOR_NO_RESPONSE * premium;
        } else { // for kind response
            payoutAmount = 0;
        }
    }
}