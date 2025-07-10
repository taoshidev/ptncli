import typer
from .list import list_command
from .register import register

app = typer.Typer(help="Subnet operations")

app.command(name="list")(list_command)
app.command(name="register")(register)

__all__ = ["app"]