import typer
import getpass
from typing import Optional
from bittensor_wallet import Wallet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ptncli.utils.api import make_api_request

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
    wallet = Wallet(name=wallet_name, path=wallet_path)
    password = getpass.getpass(prompt='Re-enter wallet password: ')
    
    coldkey = wallet.get_coldkey(password=password)
    hotkey = wallet.get_hotkey(password=password)
    
    # Show withdrawal details
    console.print(f"[cyan]Amount to withdraw:[/cyan] {amount}")
    console.print(f"[cyan]Wallet:[/cyan] {wallet_name}")
    console.print(f"[cyan]Miner address:[/cyan] {hotkey.ss58_address}")
    
    if prompt:
        confirm = typer.confirm(f"Are you sure you want to withdraw {amount} collateral for miner {hotkey.ss58_address}?")
        if not confirm:
            console.print("[yellow]Withdrawal cancelled[/yellow]")
            return False
    
    # Prepare payload for withdrawal
    payload = {
        "amount": amount,
        "miner_address": hotkey.ss58_address
    }
    
    # Make the API request
    console.print("\n[cyan]Sending withdrawal request...[/cyan]")
    
    try:
        response = make_api_request("/collateral/withdraw", payload)
        
        if response is None:
            console.print("[red]❌ Withdrawal request failed[/red]")
            return False
        
        # Check if withdrawal was successful
        if response.get("success", False):
            console.print("[green]✅ Collateral withdrawal successful![/green]")
            
            # Show success panel
            success_panel = Panel.fit(
                f"🎉 Withdrawal completed!\nAmount: {amount}\nMiner: {hotkey.ss58_address}",
                style="bold green",
                border_style="green"
            )
            console.print(success_panel)
            return True
        else:
            error_msg = response.get("error", "Unknown error occurred")
            console.print(f"[red]❌ Withdrawal failed: {error_msg}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error during withdrawal: {e}[/red]")
        return False