import typer
from .add import add_command
from .list import list_command

app = typer.Typer(help="Stake management operations")

app.command(name="add")(add_command)
app.command(name="list")(list_command)

__all__ = ["app"]