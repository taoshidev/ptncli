import asyncio
import typer
from bittensor_cli.src.commands import wallets

def list_command(
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet-path",
        "--path",
        "--wallet_path",
        "--wallet.path",
        help="Path to wallets directory"
    )
):
    """List all wallets"""
    asyncio.run(extended_wallet_list(wallet_path))

async def extended_wallet_list(wallet_path: str = "~/.bittensor/wallets"):
    """
    Extended wallet list that shows wallets with registration information.

    Args:
        wallet_path: Path where wallets are stored (default: ~/.bittensor/wallets)
    """
    # Call the existing wallet list functionality directly
    result = await wallets.wallet_list(wallet_path, json_output=False)

    # Add registration-specific logic here
    print("\nRegistration status checking would be implemented here")

    return result

