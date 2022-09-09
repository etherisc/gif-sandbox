// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "./FireOracle.sol";
import "@etherisc/gif-interface/contracts/components/Product.sol";

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
        address registry,
        uint256 riskpoolId,
        uint256 oracleId
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

    function applyForPolicy
        (address policyHolder, 
        uint256 premium, 
        uint256 sumInsured,
        string calldata objectName
    ) 
        external 
        payable 
        returns (bytes32 processId, uint256 requestId) 
    {
        // Validate input parameters
        require(premium > 0, "ERROR:FI-001:INVALID_PREMIUM");
        require(policyHolder != address(0), "ERROR:FI-002:POLICY_HOLDER_ZERO");
        require(!activePolicy[objectName], "ERROR:FI-003:ACTIVE_POLICY_EXISTS");

        bytes memory metaData = "";
        bytes memory applicationData = abi.encode(objectName);

        processId = _newApplication(
            policyHolder, 
            premium, 
            sumInsured,
            metaData,
            applicationData);
        _underwrite(processId);

        // Update activ state for object
        activePolicy[objectName] = true;

        // trigger fire observation for object id via oracle call
        requestId = _request(
            processId,
            abi.encode(objectName),
            CALLBACK_METHOD_NAME,
            fireOracleId
        );

        emit LogFirePolicyCreated(policyHolder, objectName, processId);
    }

    function expirePolicy(bytes32 processId) external {
        // Get policy data 
        IPolicy.Application memory application = _getApplication(processId);
        (string memory objectName) = abi.decode(application.data, (string));

        // Validate input parameter
        require(application.premiumAmount > 0, "ERROR:FI-004:NON_EXISTING_POLICY");
        require(activePolicy[objectName], "ERROR:FI-005:EXPIRED_POLICY");

        _expire(processId);
        activePolicy[objectName] = false;

        emit LogFirePolicyExpired(objectName, processId);
    }

    function oracleCallback(uint256 requestId, bytes32 processId, bytes calldata response)
        external
        onlyOracle
    {
        emit LogFireOracleCallbackReceived(requestId, processId, response);

        // Get policy data for oracle response
        IPolicy.Application memory application = _getApplication(processId);
        (string memory objectName) = abi.decode(application.data, (string));

        // Validate input parameter
        require(activePolicy[objectName], "ERROR:FI-006:EXPIRED_POLICY");

        // Get oracle response data
        (bytes1 fireCategory) = abi.decode(response, (bytes1));

        // Claim handling based on reponse to greeting provided by oracle 
        _handleClaim(processId, application.premiumAmount, fireCategory);
    }

    function _handleClaim(
        bytes32 processId, 
        uint256 premium, 
        bytes1 fireCategory
    ) 
        internal 
    {
        uint256 payoutAmount = _calculatePayoutAmount(premium, fireCategory);

        // Ensure available capital
        require(payoutAmount < address(this).balance, "ERROR:FI-007:INSOLVENT_PRODUCT");

        // no claims handling for payouts == 0
        uint256 claimId = _newClaim(processId, payoutAmount, "");
        _confirmClaim(processId, claimId, payoutAmount);

        emit LogFireClaimConfirmed(processId, claimId, payoutAmount);

        if (payoutAmount > 0) {
            uint256 payoutId = _newPayout(processId, claimId, payoutAmount, "");
            _processPayout(processId, payoutId);

            emit LogFirePayoutExecuted(processId, claimId, payoutId, payoutAmount);
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