// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.7.6;


interface IRegistryFacade {

    function getContract(bytes32 contractName)
        external
        view
        returns (address contractAddress);
}
