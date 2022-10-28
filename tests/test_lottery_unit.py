from audioop import add
from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy import deploy_lottery
from scripts.helpful_script import LOCAL_BLOCKCHAIN_ENVIROMENTS, get_account, fund_with_link, get_contract
from web3 import Web3
import pytest


def test_get_entrance_fee():
    # on the unit test, we just wanna run it on a local enviroment chainlink
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    #arrange
    lottery = deploy_lottery()
    #act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert entrance_fee == expected_entrance_fee


#require is not met, cannot start
def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    #arrange
    lottery = deploy_lottery()
    #act/assert
    #cannot start so raise a exception
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({
            "from": get_account(),
            "value": lottery.getEntranceFee()
        })


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    #act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    #assert  ???players(0)
    # to assure that we already push the account into the array
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    #act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # because the lottery.sol end lottery just changed the lottery status into calculating the winner
    # so we just need to know if the status was changed
    assert lottery.lottery_assert() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery({
        "from": get_account(index=1),
        "value": lottery.getEntranceFee()
    })
    lottery.enterLottery({
        "from": get_account(index=2),
        "value": lottery.getEntranceFee()
    })
    lottery.enterLottery({
        "from": get_account(index=3),
        "value": lottery.getEntranceFee()
    })
    lottery.enterLottery({
        "from": get_account(index=4),
        "value": lottery.getEntranceFee()
    })

    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account})

    starting_balance_of_account = account.balance()
    balance_of_account = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance(
    ) == starting_balance_of_account + balance_of_account
