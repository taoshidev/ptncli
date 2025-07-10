import typer
from .list import list_command
from .overview import overview_command
from .new_coldkey import new_coldkey_command
from .new_hotkey import new_hotkey_command

app = typer.Typer(help="Extended Bittensor wallet operations")

app.command(name="list")(list_command)
app.command(name="overview")(overview_command)
app.command(name="new_coldkey")(new_coldkey_command)
app.command(name="new_hotkey")(new_hotkey_command)

__all__ = ["app"]