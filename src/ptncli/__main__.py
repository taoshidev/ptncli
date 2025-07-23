import typer
import sys
import tomllib
from pathlib import Path

def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "unknown"

def version_callback(value: bool):
    """Callback for version flag"""
    if value:
        typer.echo(f"ptncli version: {get_version()}")
        raise typer.Exit()

def help_callback(value: bool):
    """Callback for version flag"""
    if value:
        typer.echo("ken")
        raise typer.Exit()

# Create the main app without importing command modules initially
app = typer.Typer(
    help="PTN CLI - PTN utilities",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Load commands at module level
from .commands.wallet import app as wallet_app
from .commands.subnets import app as subnets_app
from .commands.stake import app as stake_app
from .commands.collateral import app as collateral_app

app.add_typer(wallet_app, name="wallet", help="Wallet operations")
app.add_typer(subnets_app, name="subnets", help="Subnet operations")
app.add_typer(stake_app, name="stake", help="Stake operations")
app.add_typer(collateral_app, name="collateral", help="Collateral operations")

@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    ),
    help: bool = typer.Option(
        False,
        "--help",
        "-h",
        callback=help_callback,
        is_eager=True,
        help="Show help and exit"
    )
):
    """Main entry point for ptncli."""
    pass

if __name__ == "__main__":
    app()
