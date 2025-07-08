from bittensor_wallet import Wallet
from collateral_sdk import CollateralManager, Network

# ============================================= Preparation
manager = CollateralManager(Network.TESTNET)




# ============================================= On Miner Side
wallet = Wallet(name='validator')

coldkey = wallet.get_coldkey()
hotkey = wallet.get_hotkey()

# Check the current stakes.
# manager.subtensor_api.staking.get_stake_for_coldkey(wallet.coldkey.ss58_address)

# Use the first stake as the source stake.
source_stake = manager.subtensor_api.staking.get_stake_for_coldkey(coldkey.ss58_address)

print(f" source_stake: {source_stake}")


# ============================================= Deposit
# Check the current deposit.
balance = manager.balance_of(coldkey.ss58_address)

print(f"balance: {balance}")

# Create an extrinsic for a stake transfer.
extrinsic = manager.create_stake_transfer_extrinsic(
    amount=10 * 10**9,
    dest=coldkey.ss58_address,
    source_stake=source_stake[0].hotkey_ss58, # pyright: ignore[reportIndexIssue]
    source_wallet=wallet,
)

extrinsic.value
