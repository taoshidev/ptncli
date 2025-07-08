import typer
from .list import app as list_app
from .register import register

app = typer.Typer(help="Subnet operations")

app.add_typer(list_app, name="list")
app.command(name="register")(register)

__all__ = ["app"]