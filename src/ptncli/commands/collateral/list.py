import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from ptncli.utils.api import make_api_request

console = Console()

def list_command(
    miner_address: str = typer.Option(
        ...,
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
        help="Name of the wallet (for display purposes)",
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
        
        # Show query details
        console.print(f"[cyan]Miner address:[/cyan] {miner_address}")
        
        if wallet_name:
            console.print(f"[cyan]Wallet:[/cyan] {wallet_name}")
        
        console.print("")
    
    # Make the API request
    endpoint = f"/collateral/balance/{miner_address}"
    
    try:
        response = make_api_request(endpoint, method="GET", dev_mode=dev_mode)
        
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
        balance_rao = response.get("balance_rao", 0)
        balance_theta = response.get("balance_theta", 0.0)
        
        # Create a table for the results
        table = Table(title="Collateral Balance Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Miner Address", miner_address)
        table.add_row("Collateral Balance (RAO)", str(balance_rao))
        table.add_row("Collateral Balance (THETA)", str(balance_theta))
        
        if wallet_name:
            table.add_row("Wallet Name", wallet_name)
        
        console.print(table)
        
        # Show success message (only in dev mode)
        if response.get("success", True):
            if dev_mode:
                console.print("[green]✅ Collateral balance retrieved successfully![/green]")
            return True
        else:
            error_msg = response.get("error", "Unknown error occurred")
            console.print(f"[red]❌ Error: {error_msg}[/red]")
            return False
            
    except Exception as e:
        if json_output:
            console.print(f'{{"error": "Exception occurred: {e}", "success": false}}')
        else:
            console.print(f"[red]❌ Error retrieving collateral balance: {e}[/red]")
        return False