import getpass
import json

from rich.panel import Panel

from bittensor_wallet import Wallet
from bittensor_cli.src.bittensor.utils import console

from ptn_cli.src.config import PTN_API_BASE_URL_MAINNET, PTN_API_BASE_URL_TESTNET
from ptn_cli.src.utils.api import make_api_request

async def select(
    wallet: Wallet,
    network: str,
    asset: str,
    prompt: bool,
    quiet: bool = False,
    verbose: bool = False,
    json_output: bool = False
):
    # Load wallet and get keys
    password = getpass.getpass(prompt='Enter your password: ')

    coldkey = wallet.get_coldkey(password=password)
    hotkey = wallet.hotkey

    # Prepare withdrawal data for signing
    asset_selection_data = {
        "asset_selection": asset,
        "miner_coldkey": coldkey.ss58_address,
        "miner_hotkey": hotkey.ss58_address
    }

    # Create message to sign (sorted JSON)
    message = json.dumps(asset_selection_data, sort_keys=True)

    # Sign the message with coldkey
    signature = coldkey.sign(message.encode('utf-8')).hex()

    # Prepare payload for withdrawal (include signature)
    payload = {
        "asset_selection": asset,
        "miner_coldkey": coldkey.ss58_address,
        "miner_hotkey": hotkey.ss58_address,
        "signature": signature
    }

    # Determine which API base URL to use based on network
    base_url = PTN_API_BASE_URL_TESTNET if network == "test" else PTN_API_BASE_URL_MAINNET

    # Make the API request
    console.print("\n[cyan]Sending asset selection request...[/cyan]")
    console.print(f"[dim]Using network: {network}[/dim]")

    try:
        response = make_api_request("/asset-selection", payload, base_url=base_url)

        if response is None:
            console.print("[red]Asset class selection failed[/red]")
            return False

        # Check if asset selection was successful
        if response.get("successfully_processed"):
            console.print(f"[green]✅ Asset selection successful! Selected: {asset}[/green]")

            return True
        else:
            error_message = (
                response.get("error_message") or
                response.get("error") or
                "An unknown error occurred."
            )
            console.print(f"[red]❌ Asset selection failed: {error_message}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Error during asset selection: {e}[/red]")


