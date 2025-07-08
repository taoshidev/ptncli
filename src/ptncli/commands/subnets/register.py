import asyncio
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

from collateral_sdk import CollateralManager, Network

console = Console()

async def add_collateral(wallet_name: str):
  manager = CollateralManager(Network.TESTNET)
  wallet = Wallet(name=wallet_name)

  coldkey = wallet.get_coldkey()
  hotkey = wallet.get_hotkey()

  with Progress(
      SpinnerColumn(),
      TextColumn("[progress.description]{task.description}"),
      console=console,
  ) as progress:
      task = progress.add_task("Fetching stake information...", total=None)
      source_stake = manager.subtensor_api.staking.get_stake_for_coldkey(coldkey.ss58_address)
      
      progress.update(task, description="Checking balance...")
      balance = manager.balance_of(coldkey.ss58_address)
      progress.stop()

  # Create a table to display wallet information
  table = Table(title="Wallet Information", show_header=True, header_style="bold magenta")
  table.add_column("Property", style="cyan", no_wrap=True)
  table.add_column("Value", style="green")
  
  table.add_row("Coldkey Address", coldkey.ss58_address)
  table.add_row("Hotkey Address", hotkey.ss58_address)
  table.add_row("Source Stake", str(source_stake) if source_stake else "None")
  table.add_row("Balance", str(balance))
  
  console.print(table)

  # Check if source_stake is empty to avoid index error
  if not source_stake:
      console.print("[red]❌ No source stake found for this coldkey[/red]")
      return None

  console.print("[yellow]🔄 Creating stake transfer extrinsic...[/yellow]")
  
  # Create an extrinsic for a stake transfer.
  extrinsic = manager.create_stake_transfer_extrinsic(
      amount=10 * 10**9,
      dest=coldkey.ss58_address,
      source_stake=source_stake[0].hotkey_ss58, # pyright: ignore[reportIndexIssue]
      source_wallet=wallet,
  )

  return extrinsic.value

def register(
    wallet_name: str = typer.Option(
        None,
        "--wallet.name",
        help="Name of the wallet to use for registration",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet.path",
        help="Path to the wallet directory",
    ),
    netuid: int = typer.Option(
        8,
        "--netuid",
        help="Network UID to register to",
    ),
    network: Optional[str] = typer.Option(
        'test',
        "--network",
        "--subtensor.network",
        "--chain",
        "--subtensor.chain_endpoint",
        help="The subtensor network to connect to. Default: finney.",
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
    """Add collateral to the wallet"""
    
    # Display the main title with Rich Panel
    title = Text("🔗 PROPRIETARY TRADING NETWORK 🔗", style="bold blue")
    subtitle = Text("Registration & Collateral Setup", style="italic cyan")
    
    panel = Panel.fit(
        f"{title}\n{subtitle}",
        style="bold blue",
        border_style="bright_blue"
    )
    console.print(panel)
    
    console.print("\n[yellow]🔄 Decrypting wallet...[/yellow]")
    
    try:
        result = asyncio.run(add_collateral(wallet_name=wallet_name))
        if result is None:
            console.print("[red]❌ Collateral setup failed[/red]")
            return False
        console.print("[green]✅ Collateral added successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error adding collateral: {e}[/red]")
        return False

    console.print("\n[yellow]🔄 Initiating subnet registration...[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Registering to subnet...", total=None)
        
        try:
            result = asyncio.run(register_subnet(
                wallet_name=wallet_name,
                wallet_path=wallet_path,
                netuid=netuid,
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

async def register_subnet(
    wallet_name: str,
    wallet_path: str,
    netuid: int = 8,
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
        netuid: Network UID to register to
        network: Network to connect to (e.g., 'finney', 'test', 'local')
        era: Era to register for (optional)
        json_output: Whether to output as JSON
        prompt: Whether to prompt for confirmation
    """
    # Initialize wallet
    wallet = Wallet(name=wallet_name, path=wallet_path)

    # Initialize subtensor connection
    if network:
        subtensor = SubtensorInterface(network)
    else:
        subtensor = SubtensorInterface("test")  # Default to finney network

    try:
        async with subtensor:
            # Call the bittensor CLI register function
            return await subnets.register(
                wallet=wallet,
                subtensor=subtensor,
                netuid=netuid,
                era=era,
                json_output=json_output,
                prompt=prompt,
            )
    except Exception as e:
        print(f"Error registering to subnet: {e}")
        return False
