import asyncio
import getpass
import typer
from typing import Optional
from bittensor_wallet import Wallet
from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface
from bittensor_cli.src.commands.subnets import subnets
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import time

from ptncli.utils.collateral import add_collateral

console = Console()


# =================== hotkey needs to be registered
# =================== need to have stake on hotkey
# if not registered, throw warning
# get stake


async def register_subnet(
    wallet: Wallet,
    network: Optional[str] = None,
    era: Optional[int] = None,
    json_output: bool = False,
    prompt: bool = True,
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
        subtensor = SubtensorInterface("test")

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
    wallet_hotkey: str = typer.Option(
        None,
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
        'test',
        "--network",
        "--subtensor.network",
        "--chain",
        "--subtensor.chain_endpoint",
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
    prompt: bool = typer.Option(
        True,
        "--prompt/--no-prompt",
        help="Whether to prompt for confirmation",
    ),
):
    # Set netuid based on network
    netuid = 116 if network == 'test' else 8

    # Display the main title with Rich Panel
    title = Text("🔗 PROPRIETARY TRADING NETWORK 🔗", style="bold blue")
    subtitle = Text("Registration & Collateral Setup", style="italic cyan")

    wallet = Wallet(name=wallet_name, path=wallet_path)

    panel = Panel.fit(
        f"{title}\n{subtitle}",
        style="bold blue",
        border_style="bright_blue"
    )
    console.print(panel)

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
                prompt=prompt,
            ))

            progress.stop()

            if result:
                console.print("[green]✅ Registration completed successfully![/green]")

                # Show success panel
                success_panel = Panel.fit(
                    "🎉 Welcome to the Proprietary Trading Network!\nYour registration is complete.",
                    style="bold green",
                    border_style="green"
                )
                console.print(success_panel)
            else:
                console.print("[red]❌ Registration failed[/red]")
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error during registration: {e}[/red]")
            return False

    console.print("\n[yellow]🔄 Decrypting wallet...[/yellow]")

    try:
        result = asyncio.run(add_collateral(wallet=wallet, network=network or 'test'))
        print(result)

        if result is None:
            console.print("[red]❌ Collateral setup failed[/red]")
            return False
        console.print("[green]✅ Collateral added successfully[/green]")
        #
        # =================================================== hitting api
        #
    except Exception as e:
        console.print(f"[red]❌ Error adding collateral: {e}[/red]")
        return False
