import imp
from brownie import Lottery, accounts, config, network
from web3 import Web3
import pytest
import time
from scripts.deploy import deploy_lottery
from scripts.helpful_script import LOCAL_BLOCKCHAIN_ENVIROMENTS, fund_with_link, get_account
# run on a real net


def test_get_entrance_fee():
    account = accounts[0]
    print("starting testing")
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    #print("lottery.getEntranceFee()" + lottery.getEntranceFee())
    assert lottery.getEntranceFee() > 18, Web3.toWei(0.0284, "ether")
    assert lottery.getEntranceFee() < 18, Web3.toWei(0.0290, "ether")


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    Lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
