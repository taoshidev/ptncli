import typer
from .add import add_command

app = typer.Typer(help="Stake management operations")

app.command(name="add")(add_command)

__all__ = ["app"]