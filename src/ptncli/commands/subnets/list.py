import asyncio
import typer
from typing import Optional
from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface
from bittensor_cli.src.commands.subnets import subnets

app = typer.Typer()

@app.command()
def main(
    network: Optional[str] = typer.Option(
        None,
        "--network",
        "--subtensor.network",
        "--chain",
        "--subtensor.chain_endpoint",
        help="The subtensor network to connect to. Default: finney.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose output.",
    ),
    live: bool = typer.Option(
        False,
        "--live",
        help="Display live view of the table",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result as JSON.",
    ),
):
    """List all subnets and their detailed information"""
    asyncio.run(list_subnets(
        network=network,
        verbose=verbose,
        live_mode=live,
        json_output=json_output,
    ))

async def list_subnets(
    network: Optional[str] = None,
    reuse_last: bool = False,
    html_output: bool = False,
    no_cache: bool = False,
    verbose: bool = False,
    live_mode: bool = False,
    json_output: bool = False,
):
    """
    List all subnets and their detailed information.

    Args:
        network: Network to connect to (e.g., 'finney', 'test', 'local')
        reuse_last: Whether to reuse cached data
        html_output: Whether to output as HTML
        no_cache: Whether to disable caching
        verbose: Whether to show verbose output
        live_mode: Whether to show live updating data
        json_output: Whether to output as JSON
    """
    # Initialize subtensor connection
    if network:
        subtensor = SubtensorInterface(network)
    else:
        subtensor = SubtensorInterface("finney")  # Default to finney network

    try:
        async with subtensor:
            # Call the bittensor CLI subnets list function
            return await subnets.subnets_list(
                subtensor=subtensor,
                reuse_last=reuse_last,
                html_output=html_output,
                no_cache=no_cache,
                verbose=verbose,
                live=live_mode,
                json_output=json_output,
            )
    except Exception as e:
        print(f"Error listing subnets: {e}")
        return False

if __name__ == "__main__":
    app()