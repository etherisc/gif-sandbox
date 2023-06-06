// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.2;

import "@etherisc/gif-interface/contracts/components/Product.sol";

import "./FireOracle.sol";

contract FireProduct is Product {
    // constants
    bytes32 public constant VERSION = "0.0.1";
    bytes32 public constant POLICY_FLOW = "PolicyDefaultFlow";

    // leads to %5 premiums on object value
    uint256 public constant OBJECT_VALUE_DIVISOR = 20;

    // payout specs
    uint256 public constant PAYOUT_FACTOR_MEDIUM = 5;
    uint256 public constant PAYOUT_FACTOR_LARGE = 100;

    string public constant CALLBACK_METHOD_NAME = "oracleCallback";

    // variables
    // TODO should be framework feature
    bytes32[] private _applications; // useful for debugging, might need to get rid of this
    uint256 public _oracleId;

    mapping(string => bool) public activePolicy;

    // events
    event LogFirePolicyCreated(
        bytes32 processId,
        address policyHolder,
        uint256 sumInsured,
        string objectName
    );
    event LogFirePolicyExpired(string objectName, bytes32 processId);
    event LogFireOracleCallbackReceived(
        uint256 requestId,
        bytes32 processId,
        bytes fireCategory
    );
    event LogFireClaimConfirmed(
        bytes32 processId,
        uint256 claimId,
        uint256 payoutAmount
    );
    event LogFirePayoutExecuted(
        bytes32 processId,
        uint256 claimId,
        uint256 payoutId,
        uint256 payoutAmount
    );

    constructor(
        bytes32 productName,
        address token,
        uint256 oracleId,
        uint256 riskpoolId,
        address registry
    ) Product(productName, token, POLICY_FLOW, riskpoolId, registry) {
        _oracleId = oracleId;
    }

    function applications()
        external
        view
        returns (uint256 numberOfApplications)
    {
        return _applications.length;
    }

    function getApplicationId(
        uint256 idx
    ) external view returns (bytes32 processId) {
        require(
            idx < _applications.length,
            "ERROR:FI-001:APPLICATION_INDEX_TOO_LARGE"
        );
        return _applications[idx];
    }

    function decodeApplicationParameterFromData(
        bytes memory data
    ) public pure returns (string memory objectName) {
        return abi.decode(data, (string));
    }

    function encodeApplicationParametersToData(
        string memory objectName
    ) public pure returns (bytes memory data) {
        return abi.encode(objectName);
    }

    function applyForPolicy(
        string memory objectName,
        uint256 objectValue
    ) external returns (bytes32 processId, uint256 requestId) {
        // Validate input parameters
        require(objectValue > 0, "ERROR:FI-010:OBJECT_VALUE_ZERO");
        require(!activePolicy[objectName], "ERROR:FI-011:ACTIVE_POLICY_EXISTS");

        // Create and underwrite new application
        address policyHolder = msg.sender;
        uint256 premiumAmount = calculatePremium(objectValue);
        uint256 sumInsuredAmount = objectValue;
        bytes memory metaData = "";
        bytes memory applicationData = encodeApplicationParametersToData(
            objectName
        );

        processId = _newApplication(
            policyHolder,
            premiumAmount,
            sumInsuredAmount,
            metaData,
            applicationData
        );

        _underwrite(processId);

        // Update activ state for object
        activePolicy[objectName] = true;
        _applications.push(processId);

        // trigger fire observation for object id via oracle call
        requestId = _request(
            processId,
            abi.encode(objectName),
            CALLBACK_METHOD_NAME,
            _oracleId
        );

        emit LogFirePolicyCreated(
            processId,
            policyHolder,
            sumInsuredAmount,
            objectName
        );
    }

    function calculatePremium(
        uint256 objectValue
    ) public pure returns (uint256 premiumAmount) {
        return objectValue / OBJECT_VALUE_DIVISOR;
    }

    function expirePolicy(bytes32 processId) external onlyOwner {
        // Get policy data
        IPolicy.Application memory application = _getApplication(processId);
        string memory objectName = decodeApplicationParameterFromData(
            application.data
        );

        // Validate input parameter
        require(activePolicy[objectName], "ERROR:FI-005:EXPIRED_POLICY");

        _expire(processId);
        activePolicy[objectName] = false;

        emit LogFirePolicyExpired(objectName, processId);
    }

    function oracleCallback(
        uint256 requestId,
        bytes32 policyId,
        bytes calldata response
    ) external onlyOracle {
        emit LogFireOracleCallbackReceived(requestId, policyId, response);

        // Get policy data for oracle response
        /*
struct Application {
        ApplicationState state;
        uint256 premiumAmount;
        uint256 sumInsuredAmount;
        bytes data; 
        uint256 createdAt;
        uint256 updatedAt;
    }
*/

        IPolicy.Application memory applicationData = _getApplication(policyId);
        uint256 sumInsured = applicationData.sumInsuredAmount;
        string memory objectName = decodeApplicationParameterFromData(
            applicationData.data
        );
        address payable policyHolder = payable(_getMetadata(policyId).owner);

        // Validate input parameter
        require(activePolicy[objectName], "ERROR:FI-006:EXPIRED_POLICY");

        // Get oracle response data
        bytes1 fireCategory = abi.decode(response, (bytes1));

        // Claim handling based on reponse to greeting provided by oracle
        _handleClaim(policyId, policyHolder, sumInsured, fireCategory);
    }

    function getOracleId() external view returns (uint256 oracleId) {
        return _oracleId;
    }

    function _handleClaim(
        bytes32 policyId,
        address payable policyHolder,
        uint256 sumInsured,
        bytes1 fireCategory
    ) internal {
        uint256 payoutAmount = _calculatePayoutAmount(sumInsured, fireCategory);

        // no claims handling for payouts == 0
        if (payoutAmount > 0) {
            uint256 claimId = _newClaim(policyId, payoutAmount, "");
            _confirmClaim(policyId, claimId, payoutAmount);

            emit LogFireClaimConfirmed(policyId, claimId, payoutAmount);

            uint256 payoutId = _newPayout(policyId, claimId, payoutAmount, "");
            emit LogFireClaimConfirmed(policyId, claimId, payoutAmount);
            _processPayout(policyId, payoutId);

            emit LogFirePayoutExecuted(
                policyId,
                claimId,
                payoutId,
                payoutAmount
            );
        }
    }

    function _calculatePayoutAmount(
        uint256 sumInsured,
        bytes1 fireCategory
    ) internal pure returns (uint256 payoutAmount) {
        if (fireCategory == "M") {
            payoutAmount = (PAYOUT_FACTOR_MEDIUM * sumInsured)  / 100;
        } else if (fireCategory == "L") {
            payoutAmount = (PAYOUT_FACTOR_LARGE * sumInsured) / 100;
        } else {
            // small fires considered below deductible, no payout
            payoutAmount = 0;
        }
    }
}
