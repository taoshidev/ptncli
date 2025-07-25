import asyncio
import getpass
import json
import typer
from typing import Any, Dict, Optional
from bittensor_wallet import Wallet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from collateral_sdk import CollateralManager, Network
from ptncli.utils.api import make_api_request
from ptncli.config import PTN_API_BASE_URL_TESTNET, PTN_API_BASE_URL_MAINNET, COLLATERAL_DEST_ADDRESS_TESTNET, COLLATERAL_DEST_ADDRESS_MAINNET

console = Console()

async def add_collateral(
  wallet_name: str,
  wallet_path: str,
  network: str = 'finney',
  dev: bool = False,
  amount: Optional[float] = None,
  wallet_hotkey: str = "default",
) -> Optional[Dict[str, Any]]:
  manager = CollateralManager(Network.TESTNET if network == 'test' else Network.MAINNET)

  wallet = Wallet(name=wallet_name, path=wallet_path, hotkey=wallet_hotkey)
  password = getpass.getpass(prompt='Enter wallet password: ')

  coldkey = wallet.get_coldkey(password=password) if password else wallet.coldkey
  hotkey = wallet.get_hotkey(password=password) if password else wallet.hotkey          # TODO: these passwords may not be the same?

  # Set netuid based on network
  netuid = 116 if network == 'test' else 8

  with Progress(
      SpinnerColumn(),
      TextColumn("[progress.description]{task.description}"),
      console=console,
  ) as progress:
      task = progress.add_task("Fetching stake information...", total=None)
      source_stake: Any = manager.subtensor_api.staking.get_stake_for_coldkey(coldkey.ss58_address)

      progress.update(task, description="Checking Wallet Information...")
      balance: Any = manager.balance_of(coldkey.ss58_address)
      progress.stop()

  # Create wallet info table
  table_title = "Wallet Information"
  if network == 'test':
      table_title += " (testnet)"

  table = Table(title=table_title, show_header=True, header_style="bold magenta")
  table.add_column("Property", style="cyan", no_wrap=True)
  table.add_column("Value", style="green")

  # Handle Balance object formatting
  try:
      if hasattr(balance, 'value'):
          balance_str = str(balance.value)
      elif hasattr(balance, 'free'):
          balance_str = str(balance.free)
      else:
          balance_str = repr(balance)
  except Exception:
      balance_str = repr(balance)

  # Add wallet information rows
  table.add_row("Coldkey Address", coldkey.ss58_address)
  table.add_row("Hotkey Address", hotkey.ss58_address)
  table.add_row("Balance", balance_str)

  console.print(table)

  # Display all stake information in a single table
  matching_stake = None
  if source_stake:
      # Create unified stake table
      stake_table = Table(title="Stake Information", show_header=True, header_style="bold cyan")
      stake_table.add_column("Hotkey", style="cyan", no_wrap=True)
      stake_table.add_column("Netuid", style="magenta", no_wrap=True)
      stake_table.add_column("Stake Amount", style="green", justify="right")
      stake_table.add_column("Locked", style="yellow", justify="right")
      stake_table.add_column("Registered", style="bold", justify="center")

      for stake_info in source_stake:
          if stake_info.netuid != netuid:
              continue

          # Format the hotkey address to show first 8 and last 6 characters
          formatted_hotkey = f"{stake_info.hotkey_ss58[:8]}...{stake_info.hotkey_ss58[-6:]}"

          # Highlight the target netuid row
          netuid_style = "bold green" if stake_info.netuid == netuid else "magenta"

          stake_table.add_row(
              formatted_hotkey,
              f"[{netuid_style}]{stake_info.netuid}[/{netuid_style}]",
              f"{float(stake_info.stake):.4f}",
              f"{float(stake_info.locked):.4f}",
              "✅" if stake_info.is_registered else "❌"
          )
      console.print(stake_table)

      # Set matching_stake
      matching_stake = next(
          (stake for stake in source_stake if (stake.hotkey_ss58 == hotkey.ss58_address and stake.netuid == netuid)),
          None
      )
  else:
      console.print("[yellow]No stake information available[/yellow]")


    # Check if source_stake is empty to avoid index error
  if not source_stake:
      console.print("[red]❌ No source stake found for this coldkey[/red]")
      return None

  if not matching_stake:
      console.print(f"[red]❌ No stake found for hotkey {hotkey} on netuid {netuid}[/red]")
      return None

  if dev:
    console.print("[yellow]🔄 Creating stake transfer extrinsic...[/yellow]")

  # Use provided amount or default to 1 TAO
  metagraph = manager.subtensor_api.metagraphs.metagraph(netuid=netuid)
  pool = metagraph.pool
  theta_price = pool.tao_in / pool.alpha_in

  collateral_amount = amount * theta_price if amount is not None else 0
  amount = int(collateral_amount * 10**9)

  # Use configured dest address
  dest_address = COLLATERAL_DEST_ADDRESS_TESTNET if network == 'test' else COLLATERAL_DEST_ADDRESS_MAINNET

  # Create an extrinsic for a stake transfer.
  extrinsic = manager.create_stake_transfer_extrinsic(
      amount=amount,
      dest=dest_address,
      source_stake=matching_stake.hotkey_ss58,
      source_wallet=wallet,
      wallet_password=password
  )

  if dev:
    console.print(f"extrinsic: {extrinsic}")
    console.print(json.dumps(str(extrinsic), indent=2))

  encoded = manager.encode_extrinsic(extrinsic)
  decoded = manager.decode_extrinsic(encoded)

  if dev:
    console.print("[cyan]Encoded extrinsic:[/cyan]")
    console.print(json.dumps(str(encoded), indent=2))

    console.print("[cyan]Decoded extrinsic:[/cyan]")
    console.print(json.dumps(str(decoded), indent=2))

  result_dict = {
      "encoded": encoded.hex(),
      "amount": amount,
      "coldkey": coldkey.ss58_address,
  }

  if dev:
    console.print("[cyan]Returning result:[/cyan]")
    console.print(json.dumps(result_dict, indent=2, default=str))

  return result_dict

def add_command(
    wallet_name: str = typer.Option(
        None,
        "--wallet.name",
        "--wallet-name",
        "--wallet_name",
        "--name",
        help="Name of the wallet to use for collateral",
    ),
    wallet_hotkey: str = typer.Option(
        None,
        "--wallet.hotkey",
        "--wallet-hotkey",
        "--wallet_hotkey",
        "--hotkey",
        help="Hotkey of the wallet to use for collateral",
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
        help="Amount of Theta to use for collateral (default: 1)",
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

    console.print("[blue]Adding collateral to Proprietary Trading Network[/blue]")

    try:
        result = asyncio.run(add_collateral(
          network=network or 'finney',
          dev=dev,
          amount=amount,
          wallet_path=wallet_path,
          wallet_name=wallet_name,
          wallet_hotkey=wallet_hotkey
        ))

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

            # Determine the base URL based on network
            base_url = PTN_API_BASE_URL_TESTNET if network == "test" else PTN_API_BASE_URL_MAINNET

            # Use the new API utility
            response = make_api_request("/collateral/deposit", payload, base_url=base_url)

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
