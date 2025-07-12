import asyncio
import getpass
from typing import Any
from bittensor_wallet import Wallet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from collateral_sdk import CollateralManager, Network

console = Console()

async def add_collateral(wallet: Wallet, network: str = 'test'):
  manager = CollateralManager(Network.TESTNET if network == 'test' else Network.MAINNET)

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

      progress.update(task, description="Checking balance...")
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
  if source_stake:
      for stake_info in source_stake:
          # Only show stake info for the specified network
          if stake_info.netuid == netuid:
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

  console.print("[yellow]🔄 Creating stake transfer extrinsic...[/yellow]")

  # Create an extrinsic for a stake transfer.
  extrinsic = manager.create_stake_transfer_extrinsic(
      amount=10 * 10**9,
      dest=coldkey.ss58_address,
      source_stake=source_stake[0].hotkey_ss58,
      source_wallet=wallet,
      wallet_password=password
  )

  return extrinsic.value
