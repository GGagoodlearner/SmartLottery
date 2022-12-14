from brownie import Lottery, config, network
from scripts.helpful_script import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    # account = get_account(id="freecodecamp-account")
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract('vrf_coordinator').address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False))
    print("deployed lottery")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    #remember to tx.wait(1) your last transaction!
    starting_tx.wait(1)


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    #fund the contract with the link token
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    #then end the lottery
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()