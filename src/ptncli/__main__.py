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

# Create the main app without importing command modules initially
app = typer.Typer(
    help="PTN CLI - PTN utilities",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)

def load_commands():
    """Dynamically load command modules to avoid bittensor interference during help."""
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
    )
):
    """Main entry point for ptncli."""
    # Check if we're showing top-level help
    is_help = (len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']) or len(sys.argv) == 1

    if is_help:
        # For help, manually add empty command groups to show structure
        wallet_app = typer.Typer(help="Wallet operations")
        subnets_app = typer.Typer(help="Subnet operations")
        stake_app = typer.Typer(help="Stake operations")
        collateral_app = typer.Typer(help="Collateral operations")

        app.add_typer(wallet_app, name="wallet", help="Wallet operations")
        app.add_typer(subnets_app, name="subnets", help="Subnet operations")
        app.add_typer(stake_app, name="stake", help="Stake operations")
        app.add_typer(collateral_app, name="collateral", help="Collateral operations")
    else:
        # For actual commands, load the full command modules
        load_commands()

    app()

if __name__ == "__main__":
    app()
