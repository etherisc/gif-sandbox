// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;


interface IEventFacade {

    // helloworld orcle events
    event LogHelloWorldOracleRequestReceived(uint256 requestId, string greeting);
    event LogHelloWorldOracleResponseHandled(uint256 requestId, AnswerType answer);

    enum AnswerType {Kind, None, Rude}

    // gif ipolicy events
    event LogNewMetadata(
        uint256 productId,
        bytes32 bpKey,
        PolicyFlowState state
    );

    event LogMetadataStateChanged(bytes32 bpKey, PolicyFlowState state);
    event LogNewApplication(uint256 productId, bytes32 bpKey);
    event LogApplicationStateChanged(bytes32 bpKey, ApplicationState state);
    event LogNewPolicy(bytes32 bpKey);
    event LogPolicyStateChanged(bytes32 bpKey, PolicyState state);
    event LogNewClaim(bytes32 bpKey, uint256 claimId, ClaimState state);

    event LogClaimStateChanged(
        bytes32 bpKey,
        uint256 claimId,
        ClaimState state
    );

    event LogNewPayout(
        bytes32 bpKey,
        uint256 claimId,
        uint256 payoutId,
        PayoutState state
    );

    event LogPayoutStateChanged(
        bytes32 bpKey,
        uint256 payoutId,
        PayoutState state
    );

    event LogPayoutCompleted(
        bytes32 bpKey,
        uint256 payoutId,
        PayoutState state
    );

    event LogPartialPayout(bytes32 bpKey, uint256 payoutId, PayoutState state);

    enum PolicyFlowState {Started, Paused, Finished}
    enum ApplicationState {Applied, Revoked, Underwritten, Declined}
    enum PolicyState {Active, Expired}
    enum ClaimState {Applied, Confirmed, Declined}
    enum PayoutState {Expected, PaidOut}

    // gif iquery events
    event LogOracleRequested(
        bytes32 bpKey,
        uint256 requestId,
        uint256 responsibleOracleId
    );

    event LogOracleResponded(
        bytes32 bpKey,
        uint256 requestId,
        address responder,
        bool status
    );
}