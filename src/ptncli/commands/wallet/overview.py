import asyncio
import os
import typer
from bittensor_wallet import Wallet
from bittensor_cli.src.commands import wallets
from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface

def overview_command(
    wallet_name: str = typer.Option(
        None,
        "--wallet-name",
        "--name",
        "--wallet_name",
        "--wallet.name",
        help="Name of the wallet.",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet-path",
        "--path",
        "--wallet_path",
        "--wallet.path",
        help="Path to wallets directory"
    ),
    network: str = typer.Option(
        "finney",
        "--network",
        "--net",
        help="Network to connect to"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON"
    )
):
    """Show wallet overview with balance and registration information"""
    asyncio.run(extended_wallet_overview(
        wallet_name=wallet_name,
        wallet_path=wallet_path,
        network=network,
        json_output=json_output
    ))

async def extended_wallet_overview(
    wallet_name: str,
    wallet_path: str = "~/.bittensor/wallets",
    network: str = "finney",
    json_output: bool = False
):
    """
    Extended wallet overview with balance and registration information.

    Args:
        wallet_name: Name of the wallet to show overview for
        wallet_path: Path where wallets are stored (default: ~/.bittensor/wallets)
        network: Network to connect to (default: finney)
        json_output: Whether to output result as JSON
    """
    # Expand the wallet path
    expanded_path = os.path.expanduser(wallet_path)

    # Create wallet object
    wallet = Wallet(name=wallet_name, path=expanded_path)

    print(f"Wallet Overview: {wallet_name}")
    print(f"Wallet path: {expanded_path}")
    print("=" * 50)

    try:
        # Create SubtensorInterface instance
        subtensor = SubtensorInterface(network=network)
        
        # Call the existing wallet overview functionality directly
        result = await wallets.overview(
            wallet=wallet,
            subtensor=subtensor,
            json_output=json_output
        )

        # Add your registration-specific logic here
        print("\nRegistration-specific enhancements would be implemented here")
        print("- Registration status per subnet")
        print("- Stake information")
        print("- Validator/Miner status")

        return result
    except Exception as e:
        print(f"Error getting wallet overview: {e}")
        return None

