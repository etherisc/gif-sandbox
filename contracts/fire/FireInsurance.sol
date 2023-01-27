// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "@etherisc/gif-interface/contracts/components/Product.sol";

import "./FireOracle.sol";

contract FireInsurance is Product {

    // constants
    bytes32 public constant VERSION = "0.0.1";
    bytes32 public constant POLICY_FLOW = "PolicyFlowDefault";

    uint256 public constant PAYOUT_FACTOR_MEDIUM = 5;
    uint256 public constant PAYOUT_FACTOR_LARGE = 100;

    string public constant CALLBACK_METHOD_NAME = "oracleCallback";

    // variables
    uint256 public fireOracleId;
    uint256 public uniqueIndex;

    mapping(string => bool) public activePolicy;

    // events
    event LogFirePolicyCreated(address policyHolder, string objectName, bytes32 policyId);
    event LogFirePolicyExpired(string objectName, bytes32 policyId);
    event LogFireOracleCallbackReceived(uint256 requestId, bytes32 policyId, bytes fireCategory);
    event LogFireClaimConfirmed(bytes32 policyId, uint256 claimId, uint256 payoutAmount);
    event LogFirePayoutExecuted(bytes32 policyId, uint256 claimId, uint256 payoutId, uint256 payoutAmount);

    constructor(
        bytes32 productName,
        address token,
        uint256 oracleId,
        uint256 riskpoolId,
        address registry
    )
        Product(productName, token, POLICY_FLOW, riskpoolId, registry)
    {
        fireOracleId = oracleId;
    }

    // functions
    function deposit() public payable {}
    
    function withdraw(uint256 amount) external onlyOwner {
        require(amount <= address(this).balance);

        address payable receiver;
        receiver = payable(owner());
        receiver.transfer(amount);
    }

    function applyForPolicy(string calldata objectName) 
        external 
        payable 
        returns (bytes32 policyId, uint256 requestId) 
    {
        address payable policyHolder = payable(msg.sender);
        uint256 premium = msg.value;

        // Validate input parameters
        require(premium > 0, "ERROR:FI-001:INVALID_PREMIUM");
        require(!activePolicy[objectName], "ERROR:FI-003:ACTIVE_POLICY_EXISTS");

        // Create and underwrite new application
        uint256 sumInsured = 20 * premium;
        bytes memory metaData = "";
        bytes memory applicationData = abi.encode(objectName);

        policyId = _newApplication(policyHolder, premium, sumInsured, metaData, applicationData);
        _underwrite(policyId);

        // Update activ state for object
        activePolicy[objectName] = true;

        // trigger fire observation for object id via oracle call
        requestId = _request(
            policyId,
            abi.encode(objectName),
            CALLBACK_METHOD_NAME,
            fireOracleId
        );

        emit LogFirePolicyCreated(policyHolder, objectName, policyId);
    }

    function expirePolicy(bytes32 policyId) external {
        // Get policy data 
        bytes memory applicationData = _getApplication(policyId).data;
        (
            address payable policyHolder, 
            string memory objectName, 
            uint256 premium
        ) = abi.decode(applicationData, (address, string, uint256));

        // Validate input parameter
        require(premium > 0, "ERROR:FI-004:NON_EXISTING_POLICY");
        require(activePolicy[objectName], "ERROR:FI-005:EXPIRED_POLICY");

        _expire(policyId);
        activePolicy[objectName] = false;

        emit LogFirePolicyExpired(objectName, policyId);
    }

    function oracleCallback(uint256 requestId, bytes32 policyId, bytes calldata response)
        external
        onlyOracle
    {
        emit LogFireOracleCallbackReceived(requestId, policyId, response);

        // Get policy data for oracle response
        bytes memory applicationData = _getApplication(policyId).data;
        (
            address payable policyHolder, 
            string memory objectName, 
            uint256 premium
        ) = abi.decode(applicationData, (address, string, uint256));

        // Validate input parameter
        require(activePolicy[objectName], "ERROR:FI-006:EXPIRED_POLICY");

        // Get oracle response data
        (bytes1 fireCategory) = abi.decode(response, (bytes1));

        // Claim handling based on reponse to greeting provided by oracle 
        _handleClaim(policyId, policyHolder, premium, fireCategory);
    }

    function _handleClaim(
        bytes32 policyId, 
        address payable policyHolder, 
        uint256 premium, 
        bytes1 fireCategory
    ) 
        internal 
    {
        uint256 payoutAmount = _calculatePayoutAmount(premium, fireCategory);

        // no claims handling for payouts == 0
        if (payoutAmount > 0) {
            uint256 claimId = _newClaim(policyId, payoutAmount, "");
            _confirmClaim(policyId, claimId, payoutAmount);

            emit LogFireClaimConfirmed(policyId, claimId, payoutAmount);

            uint256 payoutId = _newPayout(policyId, claimId, payoutAmount, "");
            _processPayout(policyId, payoutId);

            emit LogFirePayoutExecuted(policyId, claimId, payoutId, payoutAmount);
        }
    }

    function _calculatePayoutAmount(uint256 premium, bytes1 fireCategory) 
        internal 
        pure 
        returns(uint256 payoutAmount) 
    {
        if (fireCategory == 'M') {
            payoutAmount = PAYOUT_FACTOR_MEDIUM * premium;
        } else if (fireCategory == 'L') { 
            payoutAmount = PAYOUT_FACTOR_LARGE * premium;
        } else {
            // small fires considered below deductible, no payout
            payoutAmount = 0;
        }
    }
}