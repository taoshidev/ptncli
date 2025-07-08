import typer
from .list import app as list_app
from .overview import app as overview_app
from .new_coldkey import app as new_coldkey_app
from .new_hotkey import app as new_hotkey_app

app = typer.Typer(help="Extended Bittensor wallet operations")

app.add_typer(list_app, name="list")
app.add_typer(overview_app, name="overview")
app.add_typer(new_coldkey_app, name="new_coldkey")
app.add_typer(new_hotkey_app, name="new_hotkey")

__all__ = ["app"]