import typer
import getpass
import json
from typing import Optional
from bittensor_wallet import Wallet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ptncli.utils.api import make_api_request
from ptncli.config import PTN_API_BASE_URL_TESTNET, PTN_API_BASE_URL_MAINNET

console = Console()

def withdraw_command(
    amount: float = typer.Option(
        ...,
        "--amount",
        help="Amount to withdraw from collateral",
    ),
    wallet_name: str = typer.Option(
        ...,
        "--wallet.name",
        "--wallet-name",
        "--wallet_name",
        "--name",
        help="Name of the wallet",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet.path",
        help="Path to the wallet directory",
    ),
    wallet_hotkey: str = typer.Option(
        "default",
        "--wallet.hotkey",
        "--wallet-hotkey",
        "--wallet_hotkey",
        "--hotkey",
        help="Hotkey of the wallet",
    ),
    network: str = typer.Option(
        "finney",
        "--network",
        "--subtensor.network",
        help="Network to use (finney or test)",
    ),
    prompt: bool = typer.Option(
        True,
        "--prompt/--no-prompt",
        help="Whether to prompt for confirmation",
    ),
):
    """Withdraw collateral from the Proprietary Trading Network"""

    # Display the main title with Rich Panel
    title = Text("🔗 PROPRIETARY TRADING NETWORK 🔗", style="bold blue")
    subtitle = Text("Collateral Withdrawal", style="italic cyan")

    panel = Panel.fit(
        f"{title}\n{subtitle}",
        style="bold blue",
        border_style="bright_blue"
    )

    console.print(panel)
    console.print("[blue]Withdrawing collateral from PTN[/blue]")

    # Load wallet and get keys
    wallet = Wallet(name=wallet_name, path=wallet_path, hotkey=wallet_hotkey)
    password = getpass.getpass(prompt='Re-enter wallet password: ')

    coldkey = wallet.get_coldkey(password=password) if password else wallet.coldkey

    # Show withdrawal details
    console.print(f"[cyan]Amount to withdraw:[/cyan] {amount}")
    console.print(f"[cyan]Wallet:[/cyan] {wallet_name}")
    console.print(f"[cyan]Miner address:[/cyan] {coldkey.ss58_address}")

    if prompt:
        confirm = typer.confirm(f"Are you sure you want to withdraw {amount} Theta collateral for miner {coldkey.ss58_address}?")
        if not confirm:
            console.print("[yellow]Withdrawal cancelled[/yellow]")
            return False

    # Prepare withdrawal data for signing
    withdrawal_data = {
        "amount": amount,
        "miner_address": coldkey.ss58_address
    }

    # Create message to sign (sorted JSON)
    message = json.dumps(withdrawal_data, sort_keys=True)

    # Sign the message with coldkey
    signature = coldkey.sign(message.encode('utf-8')).hex()

    # Prepare payload for withdrawal (include signature)
    payload = {
        "amount": amount,
        "miner_address": coldkey.ss58_address,
        "signature": signature
    }

    # Determine which API base URL to use based on network
    base_url = PTN_API_BASE_URL_TESTNET if network == "test" else PTN_API_BASE_URL_MAINNET

    # Make the API request
    console.print("\n[cyan]Sending withdrawal request...[/cyan]")
    console.print(f"[dim]Using network: {network}[/dim]")

    try:
        response = make_api_request("/collateral/withdraw", payload, base_url=base_url)

        if response is None:
            console.print("[red]❌ Withdrawal request failed[/red]")
            return False

        # Check if withdrawal was successful
        if response.get("successfully_processed") is not None:
            console.print("[green]✅ Collateral withdrawal successful![/green]")

            # Show success panel
            success_panel = Panel.fit(
                f"🎉 Withdrawal completed!\nAmount: {amount}\nMiner: {coldkey.ss58_address}",
                style="bold green",
                border_style="green"
            )
            console.print(success_panel)
            return True
        else:
            error_message = (
                response.get("error_message") or
                response.get("error") or
                "An unknown error occurred."
            )
            console.print(f"[red]❌ Withdrawal failed: {error_message}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Error during withdrawal: {e}[/red]")
        return False
