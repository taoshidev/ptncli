import typer
from .commands.wallet import app as wallet_app
from .commands.subnets import app as subnets_app

app = typer.Typer(help="PTN CLI - PTN utilities")
app.add_typer(wallet_app, name="wallet", help="Wallet operations")
app.add_typer(subnets_app, name="subnets", help="Subnet operations")

def main():
    """Main entry point for ptncli."""
    app()

if __name__ == "__main__":
    main()
