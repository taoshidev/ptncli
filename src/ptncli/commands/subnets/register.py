import asyncio
import getpass
import json
import typer
from typing import Optional
from bittensor_wallet import Wallet
from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface
from bittensor_cli.src.commands.subnets import subnets
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text


console = Console()

async def register_subnet(
    wallet: Wallet,
    network: Optional[str] = None,
    era: Optional[int] = None,
    json_output: bool = False,
):
    """
    Register a neuron to a subnet by recycling TAO.

    Args:
        wallet_name: Name of the wallet to use for registration
        wallet_path: Path to the wallet directory
        network: Network to connect to (e.g., 'finney', 'test', 'local')
        era: Era to register for (optional)
        json_output: Whether to output as JSON
        prompt: Whether to prompt for confirmation
    """
    # Set netuid based on network
    netuid = 116 if network == 'test' else 8

    # Initialize subtensor connection
    if network:
        subtensor = SubtensorInterface(network)
    else:
        subtensor = SubtensorInterface("finney")  # Default to finney network

    try:
        async with subtensor:
            # Call the bittensor CLI register function without prompting to avoid hanging
            # The confirmation will be handled by the main register function
            return await subnets.register(
                wallet=wallet,
                subtensor=subtensor,
                netuid=netuid,
                era=era,
                json_output=json_output,
                prompt=False,  # Set to False to avoid hanging on confirmation prompt
            )
    except Exception as e:
        print(f"Error registering to subnet: {e}")
        return False

def register(
    wallet_name: str = typer.Option(
        None,
        "--wallet.name",
        "--wallet-name",
        "--wallet_name",
        "--name",
        help="Name of the wallet to use for registration",
    ),
    hotkey: str = typer.Option(
        "default",
        "--wallet.hotkey",
        "--wallet-hotkey",
        "--wallet_hotkey",
        "--hotkey",
        help="Name of the wallet to use for registration",
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
    era: Optional[int] = typer.Option(
        None,
        "--era",
        help="Era to register for (optional)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON.",
    ),
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Show verbose debug output",
    ),
):
    # Display the main title with Rich Panel
    title = Text("🔗 PROPRIETARY TRADING NETWORK 🔗", style="bold blue")
    subtitle = Text("Registration & Collateral Setup", style="italic cyan")

    wallet = Wallet(name=wallet_name, path=wallet_path, hotkey=hotkey)

    panel = Panel.fit(
        f"{title}\n{subtitle}",
        style="bold blue",
        border_style="bright_blue"
    )

    console.print(panel)

    console.print("[blue]Registering to Proprietary Trading Network[/blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Registering to subnet...", total=None, visible=False)

        try:
            result = asyncio.run(register_subnet(
                wallet=wallet,
                network=network,
                era=era,
                json_output=json_output,
            ))

            progress.stop()

            if result:
                console.print("[green]✅ Registration completed successfully![/green]")

                # Show success panel
                success_panel = Panel.fit(
                    "🎉 Welcome to the Proprietary Trading Network!\nYour registration is complete.\n\nTo add collateral, run: ptncli collateral add",
                    style="bold green",
                    border_style="green"
                )
                console.print(success_panel)
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error during registration: {e}[/red]")
            return False

    return result
