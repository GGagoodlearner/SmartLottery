// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public minimumUSD;
    uint256 public randomness;
    AggregatorV3Interface internal priceFeed;

    //enum for creating user-defined types in solidity, convertible from or to interger
    //0 1 2
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash;
    event RequestedRandomness(bytes32 requestId);

    /**
     * Constructor inherits VRFConsumerBase
     *
     * Network: Rinkeby
     * Chainlink VRF Coordinator address: 0xb3dCcb4Cf7a26f6cf6B120Cf5A73875B7BBc655B
     * LINK token address:                0x01BE23585060835E02B77ef475b0Cc51aA1e0709
     * Key Hash: 0x2ed0feb3e7fd2022120aa84fab1945545a9f2ffc9076fd6156fa96eaff4c1311
     */

    //  _vrfCoordinator - This is the address of the smart contract that checks whether the random number generated is truly random.
    // _link - This is the address of the link token. It varies depending on your network.
    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        minimumUSD = 50 * (10**18);
        priceFeed = AggregatorV3Interface(_priceFeed);
        //initilize the lottery with the closed position
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee());
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        //price is 8 decimal,which is referred by ETH USD
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        //minimumUSD(* a big number)/adjustgedPrice =how many Eth can buy with miniUsd
        uint256 costToEnter = (minimumUSD * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        // iterate different phrases
        //enum for creating user-defined types in solidity, convertible from or to interger
        require(lottery_state == LOTTERY_STATE.CLOSED, "can't start yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // Calls Chainlink VRF requestRandomness();
        // It also requests for a verifiable random number using the keyhash:
        bytes32 requestId = requestRandomness(keyhash, fee);
        // ???
        emit RequestedRandomness(requestId);
    }

    //override the fulfillRandomness method
    // Function fulfillRandomness() is called inside requestRandomness() function
    // The requestId is the unique id that identifies your random number on the blockchain.
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "YOU ARE NOT CALCULATING YET"
        );
        require(_randomness > 0, "randomness not found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        // transfer all the entrance fee to the winner
        recentWinner.transfer(address(this).balance);
        //reset the lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
