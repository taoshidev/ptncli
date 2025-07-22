import typer
from .withdraw import withdraw_command
from .list import list_command
from .add import add_command

app = typer.Typer(help="Collateral management operations")

app.command(name="add")(add_command)
app.command(name="withdraw")(withdraw_command)
app.command(name="list")(list_command)

__all__ = ["app"]