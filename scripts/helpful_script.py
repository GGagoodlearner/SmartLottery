from brownie import network, config, accounts, interface, MockV3Aggregator, LinkToken, Contract, VRFCoordinatorMock

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIROMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS
            or network.show_active() in FORKED_LOCAL_ENVIROMENTS):
        return accounts[0]
    # else:
    return accounts.add(config["wallets"]["from_key"])


#accounts[0] brownie ganache accounts
#accounts.add("env")  enviroment variables
#accounts.load("id")

# Dictionaries are used to store data values in key:value pairs.
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_contract(contract_name):
    #docs string, means wiil define everything about the contract
    """ This function will grab the contract address from the brownie config if defined,
    otherwise, it will deploy a mock version of the contract
    and return the mock contract

        Args:
            contract_name(string)

        Returns:
            Contract
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
            eg: MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        if len(contract_type) <= 0:
            #none of the mock price fee is deployed so start to deploy the mocks
            deploy_mocks()
        contract = contract_type[-1]
        # equals to MockV3Aggregator[-1]
    else:
        #on a real network/ testnet, just to grab its actual address, and retuen mock contract
        contract_address = config["networks"][
            network.show_active()][contract_name]
        # then get the address and abi
        contract = Contract.from_abi(contract_type._name, contract_address,
                                     contract_type.abi)
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("deployed mock")


def fund_with_link(contract_address,
                   account=None,
                   link_token=None,
                   amount=250000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # another way we can create contracts to interact with
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx= link_token_contract.tranfer(contract_address, amount, {"from": account})
    tx.wait(1)
    return tx