import asyncio
import getpass
import json
from typing import Any, Dict, Optional
from bittensor_wallet import Wallet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from collateral_sdk import CollateralManager, Network
from ..config import COLLATERAL_DEST_ADDRESS

console = Console()

async def add_collateral(wallet: Wallet, network: str = 'test', dev: bool = False, amount: Optional[float] = None) -> Optional[Dict[str, Any]]:
  manager = CollateralManager(Network.TESTNET if network == 'test' else Network.MAINNET)

  console.print("[blue]Adding Collateral[/blue]")

  password = getpass.getpass(prompt='Re-enter wallet password: ')

  coldkey = wallet.get_coldkey(password=password)
  hotkey = wallet.get_hotkey(password=password)

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

  # Create a consolidated table to display wallet information with stake details
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

  # Add stake information if available
  # Find the StakeInfo that matches the netuid
  matching_stake = None
  if source_stake:
      for stake_info in source_stake:
          # Only show stake info for the specified network
          if stake_info.netuid == netuid:
              matching_stake = stake_info

              # Format the hotkey address to show first 8 and last 6 characters
              formatted_hotkey = f"{stake_info.hotkey_ss58[:8]}...{stake_info.hotkey_ss58[-6:]}"

              table.add_row("Hotkey", formatted_hotkey)
              table.add_row("Netuid", str(stake_info.netuid))
              table.add_row("Stake Amount", f"{float(stake_info.stake):.4f}")
              table.add_row("Locked", f"{float(stake_info.locked):.4f}")
              table.add_row("Registered", "✅" if stake_info.is_registered else "❌")
  else:
      table.add_row("Stake Info", "No stake information available")

  console.print(table)

  # Check if source_stake is empty to avoid index error
  if not source_stake:
      console.print("[red]❌ No source stake found for this coldkey[/red]")
      return None

  if not matching_stake:
      console.print(f"[red]❌ No stake found for netuid {netuid}[/red]")
      return None

  if dev:
    console.print("[yellow]🔄 Creating stake transfer extrinsic...[/yellow]")

  # Use provided amount or default to 1 TAO
  collateral_amount = amount if amount is not None else 1
  amount = int(collateral_amount * 10**9)

  # Use configured dest address
  dest_address = COLLATERAL_DEST_ADDRESS
  
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
