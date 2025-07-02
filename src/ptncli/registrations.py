import asyncio
from bittensor_wallet import Wallet
from bittensor_cli.src.commands import wallets

async def extended_wallet_list():
    """
    Extended wallet list that shows wallets with registration information.
    """
    # Use default wallet path
    wallet_path = "~/.bittensor/wallets"

    # Call the existing wallet list functionality directly
    result = await wallets.wallet_list(wallet_path, json_output=False)

    # Add your registration-specific logic here
    print("\nRegistration status checking would be implemented here")

    return result

if __name__ == "__main__":
    asyncio.run(extended_wallet_list())
