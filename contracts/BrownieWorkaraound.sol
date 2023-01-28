// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.2;

// not really needed here. workaround to make brownie to include ITreasury in its scope
import "@etherisc/gif-interface/contracts/modules/ITreasury.sol";

contract BrownieWorkaround {

    ITreasury public treasury;
    
}