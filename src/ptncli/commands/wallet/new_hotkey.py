import asyncio
import os
import typer
from typing import Optional
from bittensor_wallet import Wallet
from bittensor_cli.src.commands import wallets

def new_hotkey_command(
    wallet_name: str = typer.Option(
        None,
        "--wallet-name",
        "--name",
        "--wallet_name",
        "--wallet.name",
        help="Name of the wallet.",
    ),
    hotkey_name: str = typer.Option(
        None,
        "--hotkey-name",
        "--hotkey",
        "--hotkey_name",
        "--wallet.hotkey",
        help="Name of the hotkey.",
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet-path",
        "--path",
        "--wallet_path",
        "--wallet.path",
        help="Path to wallets directory"
    ),
    n_words: int = typer.Option(
        12,
        "--n-words",
        "--words",
        "--n_words",
        "--n.words",
        help="Number of words in mnemonic"
    ),
    no_password: bool = typer.Option(
        False,
        "--no-password",
        "--no_password",
        "--no.password",
        help="Don't encrypt the hotkey with a password"
    ),
    uri: Optional[str] = typer.Option(
        None,
        "--uri",
        help="Create from URI (e.g., 'Alice', 'Bob') instead of mnemonic"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing hotkey if it exists"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON"
    )
):
    """Create a new hotkey"""
    if n_words not in [12, 15, 18, 21, 24]:
        typer.echo("Error: n_words must be one of: 12, 15, 18, 21, 24")
        raise typer.Exit(1)

    asyncio.run(extended_wallet_new_hotkey(
        wallet_name=wallet_name,
        hotkey_name=hotkey_name,
        wallet_path=wallet_path,
        n_words=n_words,
        use_password=not no_password,
        uri=uri,
        overwrite=overwrite,
        json_output=json_output
    ))

async def extended_wallet_new_hotkey(
    wallet_name: str,
    hotkey_name: str,
    wallet_path: str = "~/.bittensor/wallets",
    n_words: int = 12,
    use_password: bool = True,
    uri: str = None,
    overwrite: bool = False,
    json_output: bool = False
):
    """
    Extended hotkey creation with registration-specific features.

    Args:
        wallet_name: Name of the wallet to create hotkey for
        hotkey_name: Name of the hotkey to create
        wallet_path: Path where wallets are stored (default: ~/.bittensor/wallets)
        n_words: Number of words in mnemonic (12, 15, 18, 21, or 24)
        use_password: Whether to encrypt the hotkey with a password
        uri: Create from URI (like 'Alice', 'Bob', etc.) instead of mnemonic
        overwrite: Whether to overwrite existing hotkey
        json_output: Whether to output result as JSON
    """
    # Expand the wallet path
    expanded_path = os.path.expanduser(wallet_path)

    # Create wallet object
    wallet = Wallet(name=wallet_name, path=expanded_path, hotkey=hotkey_name)

    print(f"Creating new hotkey '{hotkey_name}' for wallet: {wallet_name}")
    print(f"Wallet path: {expanded_path}")

    # Call the existing new_hotkey functionality directly
    result = await wallets.new_hotkey(
        wallet=wallet,
        n_words=n_words,
        use_password=use_password,
        uri=uri,
        overwrite=overwrite,
        json_output=json_output
    )

    # Add your registration-specific logic here
    print("\nHotkey creation completed!")
    print("Registration-specific enhancements would be implemented here")

    return result

