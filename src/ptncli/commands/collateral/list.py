import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from bittensor_wallet import Wallet

from ptncli.utils.api import make_api_request
from ptncli.config import PTN_API_BASE_URL_TESTNET, PTN_API_BASE_URL_MAINNET

console = Console()

def list_command(
    miner_address: Optional[str] = typer.Option(
        None,
        "--miner-address",
        "--miner_address",
        help="Miner SS58 address to check collateral balance for",
    ),
    wallet_name: Optional[str] = typer.Option(
        None,
        "--wallet.name",
        "--wallet-name",
        "--wallet_name",
        "--name",
        help="Name of the wallet to use (will derive miner address from wallet)",
    ),
    wallet_hotkey: str = typer.Option(
        "default",
        "--wallet.hotkey",
        "--wallet-hotkey",
        "--wallet_hotkey",
        "--hotkey",
        help="Hotkey of the wallet",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet.path",
        "--wallet-path",
        "--wallet_path",
        "--path",
        help="Path to the wallet directory",
    ),
    network: str = typer.Option(
        "finney",
        "--network",
        "--subtensor.network",
        help="The subtensor network to connect to. Default: finney.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON",
    ),
    dev_mode: bool = typer.Option(
        False,
        "--dev",
        help="Show debug information",
    ),
):
    """List collateral balance for a miner address"""

    # Validate that either miner_address or wallet_name is provided
    if not miner_address and not wallet_name:
        if json_output:
            console.print('{"error": "Either --miner-address or --wallet.name must be provided", "success": false}')
        else:
            console.print("[red]❌ Error: Either --miner-address or --wallet.name must be provided[/red]")
        return False

    # If wallet_name is provided, derive the miner address from the wallet
    if wallet_name:
        try:
            wallet = Wallet(name=wallet_name, path=wallet_path, hotkey=wallet_hotkey)
            miner_address = wallet.get_coldkey().ss58_address
        except Exception as e:
            if json_output:
                console.print(f'{{"error": "Failed to load wallet: {e}", "success": false}}')
            else:
                console.print(f"[red]❌ Failed to load wallet '{wallet_name}': {e}[/red]")
            return False

    if not json_output:
        # Display the main title with Rich Panel
        title = Text("🔗 PROPRIETARY TRADING NETWORK 🔗", style="bold blue")
        subtitle = Text("Collateral Balance", style="italic cyan")

        panel = Panel.fit(
            f"{title}\n{subtitle}",
            style="bold blue",
            border_style="bright_blue"
        )

        console.print(panel)
        console.print("[blue]Checking collateral balance[/blue]")

    # Determine the base URL based on network
    base_url = PTN_API_BASE_URL_TESTNET if network == "test" else PTN_API_BASE_URL_MAINNET

    # Make the API request
    endpoint = f"/collateral/balance/{miner_address}"

    try:
        response = make_api_request(endpoint, method="GET", base_url=base_url, dev_mode=dev_mode)

        if response is None:
            if json_output:
                console.print('{"error": "API request failed", "success": false}')
            else:
                console.print("[red]❌ Failed to retrieve collateral balance[/red]")
            return False

        # Handle successful response
        if json_output:
            import json
            console.print(json.dumps(response))
            return True

        # Display results in a nice table format
        balance_theta = response.get("balance_theta", 0.0)

        # Create a table for the results
        table = Table(title="Collateral Balance Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        if wallet_name:
            table.add_row("Wallet Name", wallet_name)

        table.add_row("Miner Address", miner_address)
        table.add_row("Collateral Balance (THETA)", str(balance_theta))

        console.print(table)

        # Show success message (only in dev mode)
        if response is None:
            console.print("[yellow]⚠️ API call failed[/yellow]")
        else:
            if response.get("balance_theta") is not None:
                if dev_mode:
                    console.print("[green]✅ Collateral balance retrieved successfully![/green]")
                return True
            else:
                error_message = (
                    response.get("error") or
                    "An unknown error occurred."
                )
                console.print(f"[red]❌ Error: {error_message}[/red]")
                return False

    except Exception as e:
        if json_output:
            console.print(f'{{"error": "Exception occurred: {e}", "success": false}}')
        else:
            console.print(f"[red]❌ Error retrieving collateral balance: {e}[/red]")
        return False
