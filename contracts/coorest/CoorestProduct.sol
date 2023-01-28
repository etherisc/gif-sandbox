// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

import "@etherisc/gif-interface/contracts/components/Product.sol";

contract CoorestProduct is 
    Product, 
    AccessControl, 
    Initializable
{
    using EnumerableSet for EnumerableSet.Bytes32Set;

    bytes32 public constant NAME = "CoorestCo2Product";
    bytes32 public constant VERSION = "0.1";
    bytes32 public constant POLICY_FLOW = "PolicyDefaultFlow";

    bytes32 public constant INSURER_ROLE = keccak256("INSURER");

    uint256 public constant PERCENTAGE_MULTIPLIER = 2**24;

    // group policy data structure
    struct Risk {
        bytes32 id; // hash over projectId, regionId, plantId
        bytes32 projectId; // differentiate between different projects
        // bytes32 regionId; // region id
        // bytes32 plantId; // the plant id
        // TODO: add more risk parameters

        uint256 requestId;
        bool requestTriggered;
        uint256 responseAt;
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 private _oracleId;

    bytes32[] private _riskIds;
    mapping(bytes32 => Risk) /* riskId */
        private _risks;
    mapping(bytes32 => EnumerableSet.Bytes32Set) /* riskId */ /* processIds */
        private _policies;
    bytes32[] private _applications; // useful for debugging, might need to get rid of this

    event LogCoorestRiskDataCreated(
        bytes32 riskId,
        bytes32 projecId // ,
        // bytes32 regionId,
        // bytes32 plantId
    );

    event LogCoorestRiskDataRequested(
        uint256 requestId,
        bytes32 riskId,
        bytes32 projectId // ,
        // bytes32 regionId,
        // bytes32 plantId
    );

    event LogCoorestRiskDataReceived(
        uint256 requestId,
        bytes32 riskId //,
        // TODO: maybe more risk data
    );

    event LogCoorestRiskDataRequestCancelled(
        bytes32 processId,
        uint256 requestId
    );

    event LogCoorestRiskProcessed(bytes32 riskId, uint256 policies);

    event LogCoorestPolicyApplicationCreated(
        bytes32 policyId,
        address policyHolder,
        uint256 premiumAmount,
        uint256 sumInsuredAmount
    );

    event LogCoorestPolicyCreated(
        bytes32 policyId,
        address policyHolder,
        uint256 premiumAmount,
        uint256 sumInsuredAmount
    );

    event LogCoorestPolicyProcessed(bytes32 policyId);
    event LogCoorestClaimCreated(
        bytes32 policyId,
        uint256 claimId,
        uint256 payoutAmount
    );
    event LogCoorestPayoutCreated(bytes32 policyId, uint256 payoutAmount);

    constructor(
        bytes32 productName,
        address token,
        uint256 oracleId,
        uint256 riskpoolId,
        address registry
    )
        Product(productName, token, POLICY_FLOW, riskpoolId, registry)
    {
        _oracleId = oracleId;

        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
    }

    function grantInsurerRole(address insurer) 
        external
        onlyOwner
    {
        _setupRole(INSURER_ROLE, insurer);
    }

    // TODO add revokeInsurerRole

    function createRisk(
        bytes32 projectId // ,
    )
        external
        // bytes32 regionId,
        // bytes32 plantId //,
        // TODO: maybe more risk parameters
        onlyRole(INSURER_ROLE)
        returns (bytes32 riskId)
    {
        // TODO: _validateRiskParameters(...);

        riskId = calculateRiskId(projectId); // , regionId, plantId);
        _riskIds.push(riskId);

        Risk storage risk = _risks[riskId];
        require(risk.createdAt == 0, "ERROR:CO2-001:RISK_ALREADY_EXISTS");

        risk.id = riskId;
        risk.projectId = projectId;
        // risk.regionId = regionId;
        // risk.plantId = plantId;
        // TODO: maybe more risk parameters

        risk.createdAt = block.timestamp; // solhint-disable-line
        risk.updatedAt = block.timestamp; // solhint-disable-line

        emit LogCoorestRiskDataCreated(
            risk.id,
            risk.projectId //,
            // risk.regionId,
            // risk.plantId
        );
    }

    function calculateRiskId(
        bytes32 projectId //,
    )
        public
        pure
        returns (
            // bytes32 regionId,
            // bytes32 plantId
            bytes32 riskId
        )
    {
        riskId = keccak256(abi.encode(projectId)); // , regionId, plantId));
    }

    function applyForPolicy(
        address policyHolder,
        uint256 premium,
        uint256 sumInsured,
        bytes32 riskId
    ) 
        external 
        onlyRole(INSURER_ROLE)
        returns(bytes32 processId) 
    {
        Risk storage risk = _risks[riskId];
        require(risk.createdAt > 0, "ERROR:CO2-004:RISK_UNDEFINED");
        require(policyHolder != address(0), "ERROR:CO2-005:POLICY_HOLDER_ZERO");

        bytes memory metaData = "";
        bytes memory applicationData = abi.encode(riskId);

        processId = _newApplication(
            policyHolder,
            premium,
            sumInsured,
            metaData,
            applicationData
        );

        _applications.push(processId);

        emit LogCoorestPolicyApplicationCreated(
            processId,
            policyHolder,
            premium,
            sumInsured
        );

        bool success = _underwrite(processId);

        if (success) {
            EnumerableSet.add(_policies[riskId], processId);

            emit LogCoorestPolicyCreated(
                processId,
                policyHolder,
                premium,
                sumInsured
            );
        }
    }

    function underwrite(bytes32 processId)
        external
        onlyRole(INSURER_ROLE)
        returns (bool success)
    {
        // ensure the application for processId exists
        _getApplication(processId);
        success = _underwrite(processId);

        if (success) {
            IPolicy.Application memory application = _getApplication(processId);
            IPolicy.Metadata memory metadata = _getMetadata(processId);
            emit LogCoorestPolicyCreated(
                processId,
                metadata.owner,
                application.premiumAmount,
                application.sumInsuredAmount
            );
        }
    }

    function collectPremium(bytes32 policyId)
        external
        onlyRole(INSURER_ROLE)
        returns (
            bool success,
            uint256 fee,
            uint256 netPremium
        )
    {
        (success, fee, netPremium) = _collectPremium(policyId);
    }

    function triggerOracle(bytes32 processId)
        external
        onlyRole(INSURER_ROLE)
        returns (uint256 requestId)
    {
        Risk storage risk = _risks[_getRiskId(processId)];
        require(risk.createdAt > 0, "ERROR:CO2-010:RISK_UNDEFINED");
        require(risk.responseAt == 0, "ERROR:CO2-011:ORACLE_ALREADY_RESPONDED");

        bytes memory queryData = abi.encode(
            risk.projectId //,
            // risk.regionId,
            // risk.plantId
        );

        requestId = _request(processId, queryData, "oracleCallback", _oracleId);

        risk.requestId = requestId;
        risk.requestTriggered = true;
        risk.updatedAt = block.timestamp; // solhint-disable-line

        emit LogCoorestRiskDataRequested(
            risk.requestId,
            risk.id,
            risk.projectId //,
            // risk.regionId,
            // risk.plantId
        );
    }

    function cancelOracleRequest(bytes32 processId)
        external
        onlyRole(INSURER_ROLE)
    {
        Risk storage risk = _risks[_getRiskId(processId)];
        require(risk.createdAt > 0, "ERROR:CO2-012:RISK_UNDEFINED");
        require(
            risk.requestTriggered,
            "ERROR:CO2-013:ORACLE_REQUEST_NOT_FOUND"
        );
        require(risk.responseAt == 0, "ERROR:CO2-014:EXISTING_CALLBACK");

        _cancelRequest(risk.requestId);

        // reset request id to allow to trigger again
        risk.requestTriggered = false;
        risk.updatedAt = block.timestamp; // solhint-disable-line

        emit LogCoorestRiskDataRequestCancelled(processId, risk.requestId);
    }

    function oracleCallback(
        uint256 requestId,
        bytes32 processId,
        bytes calldata responseData
    ) external onlyOracle {
        bytes32 projectId = abi.decode( // bytes32 plantId //, // bytes32 regionId, //, // TODO: add parameters
            responseData,
            (bytes32) //, bytes32, bytes32)
        ); // TODO: add more args

        bytes32 riskId = _getRiskId(processId);
        require(
            riskId == calculateRiskId(projectId), //, regionId, plantId),
            "ERROR:CO2-020:RISK_ID_MISMATCH"
        );

        Risk storage risk = _risks[riskId];
        require(risk.createdAt > 0, "ERROR:CO2-021:RISK_UNDEFINED");
        require(
            risk.requestId == requestId,
            "ERROR:CO2-022:REQUEST_ID_MISMATCH"
        );
        require(risk.responseAt == 0, "ERROR:CO2-023:EXISTING_CALLBACK");

        // require(
        // TODO: check validity of response
        // );

        // update risk
        risk.responseAt = block.timestamp; // solhint-disable-line
        risk.updatedAt = block.timestamp; // solhint-disable-line

        emit LogCoorestRiskDataReceived(
            requestId,
            riskId /* TODO: add parameters here */
        );
    }

    function getOracleId() external view returns(uint256 oracleId) {
        return _oracleId;
    }


    function processPoliciesForRisk(bytes32 riskId, uint256 batchSize)
        external
        onlyRole(INSURER_ROLE)
        returns (bytes32[] memory processedPolicies)
    {
        Risk memory risk = _risks[riskId];
        require(risk.responseAt > 0, "ERROR:CO2-030:ORACLE_RESPONSE_MISSING");

        uint256 elements = EnumerableSet.length(_policies[riskId]);
        if (elements == 0) {
            emit LogCoorestRiskProcessed(riskId, 0);
            return new bytes32[](0);
        }

        if (batchSize == 0) {
            batchSize = elements;
        } else {
            batchSize = min(batchSize, elements);
        }

        processedPolicies = new bytes32[](batchSize);
        uint256 elementIdx = elements - 1;

        for (uint256 i = 0; i < batchSize; i++) {
            // grab and process the last policy
            bytes32 policyId = EnumerableSet.at(
                _policies[riskId],
                elementIdx - i
            );
            processPolicy(policyId);
            processedPolicies[i] = policyId;
        }

        emit LogCoorestRiskProcessed(riskId, batchSize);
    }

    function processPolicy(bytes32 policyId) public onlyRole(INSURER_ROLE) {
        IPolicy.Application memory application = _getApplication(policyId);
        bytes32 riskId = abi.decode(application.data, (bytes32));
        Risk memory risk = _risks[riskId];

        require(risk.id == riskId, "ERROR:CO2-031:RISK_ID_INVALID");
        require(risk.responseAt > 0, "ERROR:CO2-032:ORACLE_RESPONSE_MISSING");
        require(
            EnumerableSet.contains(_policies[riskId], policyId),
            "ERROR:CO2-033:POLICY_FOR_RISK_UNKNOWN"
        );

        EnumerableSet.remove(_policies[riskId], policyId);

        uint256 claimAmount = calculatePayout();
        // TODO: add risk parameters here
        // application.sumInsuredAmount

        uint256 claimId = _newClaim(policyId, claimAmount, "");
        emit LogCoorestClaimCreated(policyId, claimId, claimAmount);

        if (claimAmount > 0) {
            uint256 payoutAmount = claimAmount;
            _confirmClaim(policyId, claimId, payoutAmount);

            uint256 payoutId = _newPayout(policyId, claimId, payoutAmount, "");
            _processPayout(policyId, payoutId);

            emit LogCoorestPayoutCreated(policyId, payoutAmount);
        } else {
            _declineClaim(policyId, claimId);
            _closeClaim(policyId, claimId);
        }

        _expire(policyId);
        _close(policyId);

        emit LogCoorestPolicyProcessed(policyId);
    }

    function calculatePayout()
        public
        pure
        returns (
            // TODO: add parameters
            uint256 payoutAmount
        )
    {
        // TODO: add calculation logic
        payoutAmount = 0;
    }

    function calculatePayoutPercentage()
        public
        pure
        returns (
            // TODO: add parameters
            uint256 payoutPercentage
        )
    {
        // TODO: add calculation logic
        return 0;
    }

    function getPercentageMultiplier()
        external
        pure
        returns (uint256 multiplier)
    {
        return PERCENTAGE_MULTIPLIER;
    }

    function min(uint256 a, uint256 b) private pure returns (uint256) {
        return a <= b ? a : b;
    }

    function risks() external view returns (uint256) {
        return _riskIds.length;
    }

    function getRiskId(uint256 idx) external view returns (bytes32 riskId) {
        return _riskIds[idx];
    }

    function getRisk(bytes32 riskId) external view returns (Risk memory risk) {
        return _risks[riskId];
    }

    function applications() external view returns (uint256 applicationCount) {
        return _applications.length;
    }

    function getApplicationId(uint256 applicationIdx)
        external
        view
        returns (bytes32 processId)
    {
        return _applications[applicationIdx];
    }

    function policies(bytes32 riskId)
        external
        view
        returns (uint256 policyCount)
    {
        return EnumerableSet.length(_policies[riskId]);
    }

    function getPolicyId(bytes32 riskId, uint256 policyIdx)
        external
        view
        returns (bytes32 processId)
    {
        return EnumerableSet.at(_policies[riskId], policyIdx);
    }

    function getApplicationDataStructure()
        external
        pure
        override
        returns (string memory dataStructure)
    {
        return "(bytes32 riskId)";
    }

    function _validateRiskParameters() internal // add risk parameters here

    {
        // require(
        // condition,
        // message
        // );
    }

    function _processPolicy(bytes32 policyId, Risk memory risk) internal {
        IPolicy.Application memory application = _getApplication(policyId);

        uint256 claimAmount = calculatePayout();
        // TODO: add risk parameters

        uint256 claimId = _newClaim(policyId, claimAmount, "");
        emit LogCoorestClaimCreated(policyId, claimId, claimAmount);

        if (claimAmount > 0) {
            uint256 payoutAmount = claimAmount;
            _confirmClaim(policyId, claimId, payoutAmount);

            uint256 payoutId = _newPayout(policyId, claimId, payoutAmount, "");
            _processPayout(policyId, payoutId);

            emit LogCoorestPayoutCreated(policyId, payoutAmount);
        } else {
            _declineClaim(policyId, claimId);
            _closeClaim(policyId, claimId);
        }

        emit LogCoorestPolicyProcessed(policyId);
    }

    function _getRiskId(bytes32 processId)
        private
        view
        returns (bytes32 riskId)
    {
        IPolicy.Application memory application = _getApplication(processId);
        (riskId) = abi.decode(application.data, (bytes32));
    }
}
