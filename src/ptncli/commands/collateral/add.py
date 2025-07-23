import asyncio
import typer
from typing import Optional
from bittensor_wallet import Wallet
from rich.console import Console

from ptncli.utils.collateral import add_collateral
from ptncli.utils.api import make_api_request

console = Console()

def add_command(
    wallet_name: str = typer.Option(
        None,
        "--wallet.name",
        "--wallet-name",
        "--wallet_name",
        "--name",
        help="Name of the wallet to use for collateral",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet.path",
        help="Path to the wallet directory",
    ),
    network: Optional[str] = typer.Option(
        'finney',
        "--network",
        "--subtensor.network",
        help="The subtensor network to connect to. Default: test.",
    ),
    amount: Optional[float] = typer.Option(
        None,
        "--amount",
        help="Amount of TAO to use for collateral (default: 1)",
    ),
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Show verbose debug output",
    ),
):
    """
    Add collateral to the Proprietary Trading Network.
    """
    wallet = Wallet(name=wallet_name, path=wallet_path)

    console.print("[blue]Adding collateral to Proprietary Trading Network[/blue]")

    try:
        result = asyncio.run(add_collateral(wallet=wallet, network=network or 'finney', dev=dev, amount=amount))

        if dev:
            print(result)

        if result is None:
            console.print("[red]❌ Collateral setup failed[/red]")
            return False

        if dev:
            console.print("[green]✅ Extrinsic Created successfully[/green]")
            console.print("sending extrinsic")

        try:
            # Convert bytearray to hex string for JSON serialization
            encoded_data = result["encoded"]
            if isinstance(encoded_data, bytearray):
                encoded_data = encoded_data.hex()

            payload = {
                "extrinsic": encoded_data,
            }

            # Use the new API utility
            response = make_api_request("/collateral/deposit", payload)

            if response is None:
                console.print("[yellow]⚠️ API call failed[/yellow]")
            else:
                console.print("[green]✅ Collateral added successfully![/green]")

        except Exception as api_error:
            console.print(f"[yellow]⚠️ API call failed: {api_error}[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error adding collateral: {e}[/red]")
        return False

    return True
