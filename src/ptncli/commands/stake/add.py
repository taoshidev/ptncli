import asyncio
import json
import typer
from collections import defaultdict
from functools import partial
from typing import Optional, List
from async_substrate_interface.errors import SubstrateRequestException
from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface
from bittensor_wallet import Wallet
from bittensor_cli.src.bittensor.balances import Balance
from rich.table import Table
from rich.prompt import Confirm, Prompt
from bittensor_cli.src.bittensor.utils import (
    console,
    err_console,
    format_error_message,
    get_hotkey_wallets_for_wallet,
    is_valid_ss58_address,
    print_error,
    print_verbose,
    unlock_key,
    json_console,
)
from bittensor_cli.src import COLOR_PALETTE


async def stake_add(
    wallet: Wallet,
    network: str,
    stake_all: bool,
    amount: float,
    prompt: bool,
    all_hotkeys: bool,
    include_hotkeys: list[str],
    exclude_hotkeys: list[str],
    safe_staking: bool,
    rate_tolerance: float,
    allow_partial_stake: bool,
    json_output: bool,
    era: int,
):
    """
    Args:
        wallet: wallet object
        network: network to connect to
        stake_all: whether to stake all available balance
        amount: specified amount of balance to stake
        prompt: whether to prompt the user
        all_hotkeys: whether to stake all hotkeys
        include_hotkeys: list of hotkeys to include in staking process (if not specifying `--all`)
        exclude_hotkeys: list of hotkeys to exclude in staking (if specifying `--all`)
        safe_staking: whether to use safe staking
        rate_tolerance: rate tolerance percentage for stake operations
        allow_partial_stake: whether to allow partial stake
        json_output: whether to output stake info in JSON format
        era: Blocks for which the transaction should be valid.

    Returns:
        bool: True if stake operation is successful, False otherwise
    """
    # Create subtensor interface inside async context
    subtensor = SubtensorInterface(network=network)

    # Set netuid based on network
    netuid = 116 if network == 'test' else 8

    # Implementation of stake_add function
    async def safe_stake_extrinsic(
        amount_: Balance,
        current_stake: Balance,
        hotkey_ss58_: str,
        price_limit: Balance,
        netuid_: int = 8,
        status=None,
    ) -> tuple[bool, str]:
        err_out = partial(print_error, status=status)
        failure_prelude = (
            f":cross_mark: [red]Failed[/red] to stake {amount_} on Netuid {netuid_}"
        )
        current_balance, next_nonce, call = await asyncio.gather(
            subtensor.get_balance(wallet.coldkeypub.ss58_address),
            subtensor.substrate.get_account_next_index(wallet.coldkeypub.ss58_address),
            subtensor.substrate.compose_call(
                call_module="SubtensorModule",
                call_function="add_stake_limit",
                call_params={
                    "hotkey": hotkey_ss58_,
                    "netuid": netuid_,
                    "amount_staked": amount_.rao,
                    "limit_price": price_limit,
                    "allow_partial": allow_partial_stake,
                },
            ),
        )
        extrinsic = await subtensor.substrate.create_signed_extrinsic(
            call=call,
            keypair=wallet.coldkey,
            nonce=next_nonce,
            era={"period": era},
        )
        try:
            response = await subtensor.substrate.submit_extrinsic(
                extrinsic, wait_for_inclusion=True, wait_for_finalization=False
            )
        except SubstrateRequestException as e:
            if "Custom error: 8" in str(e):
                err_msg = (
                    f"{failure_prelude}: Price exceeded tolerance limit. "
                    f"Transaction rejected because partial staking is disabled. "
                    f"Either increase price tolerance or enable partial staking."
                )
                print_error("\n" + err_msg, status=status)
            else:
                err_msg = f"{failure_prelude} with error: {format_error_message(e)}"
                err_out("\n" + err_msg)
            return False, err_msg
        if not await response.is_success:
            err_msg = f"{failure_prelude} with error: {format_error_message(await response.error_message)}"
            err_out("\n" + err_msg)
            return False, err_msg
        else:
            if json_output:
                return True, ""
            block_hash = await subtensor.substrate.get_chain_head()
            new_balance, new_stake = await asyncio.gather(
                subtensor.get_balance(wallet.coldkeypub.ss58_address, block_hash),
                subtensor.get_stake(
                    hotkey_ss58=hotkey_ss58_,
                    coldkey_ss58=wallet.coldkeypub.ss58_address,
                    netuid=netuid_,
                    block_hash=block_hash,
                ),
            )
            console.print(
                f":white_heavy_check_mark: [dark_sea_green3]Finalized. "
                f"Stake added to netuid: {netuid_}[/dark_sea_green3]"
            )
            console.print(
                f"Balance:\n  [blue]{current_balance}[/blue] :arrow_right: "
                f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{new_balance}"
            )

            amount_staked = current_balance - new_balance
            if allow_partial_stake and (amount_staked != amount_):
                console.print(
                    "Partial stake transaction. Staked:\n"
                    f"  [{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{amount_staked}"
                    f"[/{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}] "
                    f"instead of "
                    f"[blue]{amount_}[/blue]"
                )

            console.print(
                f"Subnet: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]"
                f"{netuid_}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}] "
                f"Stake:\n"
                f"  [blue]{current_stake}[/blue] "
                f":arrow_right: "
                f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{new_stake}\n"
            )
            return True, ""

    async def stake_extrinsic(
        netuid_i, amount_, current, staking_address_ss58, status=None
    ) -> tuple[bool, str]:
        err_out = partial(print_error, status=status)
        current_balance, next_nonce, call = await asyncio.gather(
            subtensor.get_balance(wallet.coldkeypub.ss58_address),
            subtensor.substrate.get_account_next_index(wallet.coldkeypub.ss58_address),
            subtensor.substrate.compose_call(
                call_module="SubtensorModule",
                call_function="add_stake",
                call_params={
                    "hotkey": staking_address_ss58,
                    "netuid": netuid_i,
                    "amount_staked": amount_.rao,
                },
            ),
        )
        failure_prelude = (
            f":cross_mark: [red]Failed[/red] to stake {amount} on Netuid {netuid_i}"
        )
        extrinsic = await subtensor.substrate.create_signed_extrinsic(
            call=call, keypair=wallet.coldkey, nonce=next_nonce, era={"period": era}
        )
        try:
            response = await subtensor.substrate.submit_extrinsic(
                extrinsic, wait_for_inclusion=True, wait_for_finalization=False
            )
        except SubstrateRequestException as e:
            err_msg = f"{failure_prelude} with error: {format_error_message(e)}"
            err_out("\n" + err_msg)
            return False, err_msg
        else:
            if not await response.is_success:
                err_msg = f"{failure_prelude} with error: {format_error_message(await response.error_message)}"
                err_out("\n" + err_msg)
                return False, err_msg
            else:
                if json_output:
                    return True, ""
                new_block_hash = await subtensor.substrate.get_chain_head()
                new_balance, new_stake = await asyncio.gather(
                    subtensor.get_balance(
                        wallet.coldkeypub.ss58_address, block_hash=new_block_hash
                    ),
                    subtensor.get_stake(
                        hotkey_ss58=staking_address_ss58,
                        coldkey_ss58=wallet.coldkeypub.ss58_address,
                        netuid=netuid_i,
                        block_hash=new_block_hash,
                    ),
                )
                console.print(
                    f":white_heavy_check_mark: "
                    f"[dark_sea_green3]Finalized. Stake added to netuid: {netuid_i}[/dark_sea_green3]"
                )
                console.print(
                    f"Balance:\n  [blue]{current_balance}[/blue] :arrow_right: "
                    f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{new_balance}"
                )
                console.print(
                    f"Subnet: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]"
                    f"{netuid_i}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}] "
                    f"Stake:\n"
                    f"  [blue]{current}[/blue] "
                    f":arrow_right: "
                    f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{new_stake}\n"
                )
                return True, ""

    hotkeys_to_stake_to = _get_hotkeys_to_stake_to(
        wallet=wallet,
        all_hotkeys=all_hotkeys,
        include_hotkeys=include_hotkeys,
        exclude_hotkeys=exclude_hotkeys,
    )

    chain_head = await subtensor.substrate.get_chain_head()
    _all_subnets, _stake_info, current_wallet_balance = await asyncio.gather(
        subtensor.all_subnets(block_hash=chain_head),
        subtensor.get_stake_for_coldkey(
            coldkey_ss58=wallet.coldkeypub.ss58_address,
            block_hash=chain_head,
        ),
        subtensor.get_balance(wallet.coldkeypub.ss58_address, block_hash=chain_head),
    )
    all_subnets = {di.netuid: di for di in _all_subnets}

    hotkey_stake_map = {}
    for _, hotkey_ss58 in hotkeys_to_stake_to:
        hotkey_stake_map[hotkey_ss58] = Balance.from_rao(0)

    for stake_info in _stake_info:
        if stake_info.hotkey_ss58 in hotkey_stake_map and stake_info.netuid == netuid:
            hotkey_stake_map[stake_info.hotkey_ss58] = stake_info.stake

    rows = []
    amounts_to_stake = []
    current_stake_balances = []
    prices_with_tolerance = []
    remaining_wallet_balance = current_wallet_balance
    max_slippage = 0.0

    subnet_info = all_subnets.get(netuid)
    if not subnet_info:
        err_console.print(f"Subnet with netuid: {netuid} does not exist.")
        return False

    for hotkey in hotkeys_to_stake_to:
        current_stake_balances.append(hotkey_stake_map[hotkey[1]])

        amount_to_stake = Balance(0)
        if amount:
            amount_to_stake = Balance.from_tao(amount)
        elif stake_all:
            amount_to_stake = current_wallet_balance
        elif not amount:
            amount_to_stake, _ = _prompt_stake_amount(
                current_balance=remaining_wallet_balance,
                netuid=netuid,
                action_name="stake",
            )
        amounts_to_stake.append(amount_to_stake)

        if amount_to_stake > remaining_wallet_balance:
            err_console.print(
                f"[red]Not enough stake[/red]:[bold white]\n wallet balance:{remaining_wallet_balance} < "
                f"staking amount: {amount_to_stake}[/bold white]"
            )
            return False
        remaining_wallet_balance -= amount_to_stake

        stake_fee = await subtensor.get_stake_fee(
            origin_hotkey_ss58=None,
            origin_netuid=None,
            origin_coldkey_ss58=wallet.coldkeypub.ss58_address,
            destination_hotkey_ss58=hotkey[1],
            destination_netuid=netuid,
            destination_coldkey_ss58=wallet.coldkeypub.ss58_address,
            amount=amount_to_stake.rao,
        )

        current_price_float = float(subnet_info.price.tao)
        rate = 1.0 / current_price_float
        received_amount = rate * amount_to_stake

        base_row = [
            str(netuid),
            f"{hotkey[1]}",
            str(amount_to_stake),
            str(rate)
            + f" {Balance.get_unit(netuid)}/{Balance.get_unit(0)} ",
            str(received_amount.set_unit(netuid)),
            str(stake_fee),
        ]

        if safe_staking:
            if subnet_info.is_dynamic:
                price_with_tolerance = current_price_float * (1 + rate_tolerance)
                _rate_with_tolerance = (
                    1.0 / price_with_tolerance
                )
                rate_with_tolerance = f"{_rate_with_tolerance:.4f}"
                price_with_tolerance = Balance.from_tao(
                    price_with_tolerance
                ).rao
            else:
                rate_with_tolerance = "1"
                price_with_tolerance = Balance.from_rao(1)
            prices_with_tolerance.append(price_with_tolerance)

            base_row.extend(
                [
                    f"{rate_with_tolerance} {Balance.get_unit(netuid)}/{Balance.get_unit(0)} ",
                    f"[{'dark_sea_green3' if allow_partial_stake else 'red'}]"
                    f"{allow_partial_stake}[/{'dark_sea_green3' if allow_partial_stake else 'red'}]",
                ]
            )

        rows.append(tuple(base_row))

    table = _define_stake_table(wallet, subtensor, safe_staking, rate_tolerance)
    for row in rows:
        table.add_row(*row)
    _print_table_and_slippage(table, max_slippage, safe_staking)

    if prompt:
        if not Confirm.ask("Would you like to continue?"):
            return False
    if not unlock_key(wallet).success:
        return False

    if safe_staking:
        stake_coroutines = {}
        for i, (am, curr, price_with_tolerance) in enumerate(
            zip(amounts_to_stake, current_stake_balances, prices_with_tolerance)
        ):
            for _, staking_address in hotkeys_to_stake_to:
                if netuid == 0:
                    stake_coroutines[(netuid, staking_address)] = stake_extrinsic(
                        netuid_i=netuid,
                        amount_=am,
                        current=curr,
                        staking_address_ss58=staking_address,
                    )
                else:
                    stake_coroutines[(netuid, staking_address)] = safe_stake_extrinsic(
                        amount_=am,
                        current_stake=curr,
                        hotkey_ss58_=staking_address,
                        price_limit=price_with_tolerance,
                        netuid_=netuid,
                    )
    else:
        stake_coroutines = {}
        for i, (am, curr) in enumerate(zip(amounts_to_stake, current_stake_balances)):
            for _, staking_address in hotkeys_to_stake_to:
                stake_coroutines[(netuid, staking_address)] = stake_extrinsic(
                    netuid_i=netuid,
                    amount_=am,
                    current=curr,
                    staking_address_ss58=staking_address,
                )
    successes = defaultdict(dict)
    error_messages = defaultdict(dict)
    with console.status(f"\n:satellite: Staking on netuid: {netuid} ..."):
        for (ni, staking_address), coroutine in stake_coroutines.items():
            success, er_msg = await coroutine
            successes[ni][staking_address] = success
            error_messages[ni][staking_address] = er_msg
    if json_output:
        json_console.print(
            json.dumps({"staking_success": successes, "error_messages": error_messages})
        )

    return True


def _prompt_stake_amount(
    current_balance: Balance, netuid: int, action_name: str
) -> tuple[Balance, bool]:
    while True:
        amount_input = Prompt.ask(
            f"\nEnter the amount to {action_name}"
            f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{Balance.get_unit(netuid)}[/{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}] "
            f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}](max: {current_balance})[/{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}] "
            f"or "
            f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]'all'[/{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}] "
            f"for entire balance"
        )

        if amount_input.lower() == "all":
            return current_balance, True

        try:
            amount = float(amount_input)
            if amount <= 0:
                console.print("[red]Amount must be greater than 0[/red]")
                continue
            if amount > current_balance.tao:
                console.print(
                    f"[red]Amount exceeds available balance of "
                    f"[{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{current_balance}[/{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]"
                    f"[/red]"
                )
                continue
            return Balance.from_tao(amount), False
        except ValueError:
            console.print("[red]Please enter a valid number or 'all'[/red]")


def _get_hotkeys_to_stake_to(
    wallet: Wallet,
    all_hotkeys: bool = False,
    include_hotkeys: list[str] = None,
    exclude_hotkeys: list[str] = None,
) -> list[tuple[Optional[str], str]]:
    if all_hotkeys:
        all_hotkeys_: list[Wallet] = get_hotkey_wallets_for_wallet(wallet=wallet)
        return [
            (wallet.hotkey_str, wallet.hotkey.ss58_address)
            for wallet in all_hotkeys_
            if wallet.hotkey_str not in (exclude_hotkeys or [])
        ]

    if include_hotkeys:
        print_verbose("Staking to only included hotkeys")
        hotkeys = []
        for hotkey_ss58_or_hotkey_name in include_hotkeys:
            if is_valid_ss58_address(hotkey_ss58_or_hotkey_name):
                hotkeys.append((None, hotkey_ss58_or_hotkey_name))
            else:
                wallet_ = Wallet(
                    path=wallet.path,
                    name=wallet.name,
                    hotkey=hotkey_ss58_or_hotkey_name,
                )
                hotkeys.append((wallet_.hotkey_str, wallet_.hotkey.ss58_address))

        return hotkeys

    print_verbose(
        f"Staking to hotkey: ({wallet.hotkey_str}) in wallet: ({wallet.name})"
    )
    assert wallet.hotkey is not None
    return [(None, wallet.hotkey.ss58_address)]


def _define_stake_table(
    wallet: Wallet,
    subtensor: "SubtensorInterface",
    safe_staking: bool,
    rate_tolerance: float,
) -> Table:
    table = Table(
        title=f"\n[{COLOR_PALETTE['GENERAL']['HEADER']}]Staking to:\n"
        f"Wallet: [{COLOR_PALETTE['GENERAL']['CK']}]{wallet.name}[/{COLOR_PALETTE['GENERAL']['CK']}], "
        f"Coldkey ss58: [{COLOR_PALETTE['GENERAL']['CK']}]{wallet.coldkeypub.ss58_address}[/{COLOR_PALETTE['GENERAL']['CK']}]\n"
        f"Network: {subtensor.network}[/{COLOR_PALETTE['GENERAL']['HEADER']}]\n",
        show_footer=True,
        show_edge=False,
        header_style="bold white",
        border_style="bright_black",
        style="bold",
        title_justify="center",
        show_lines=False,
        pad_edge=True,
    )

    table.add_column("Netuid", justify="center", style="grey89")
    table.add_column(
        "Hotkey", justify="center", style=COLOR_PALETTE["GENERAL"]["HOTKEY"]
    )
    table.add_column(
        f"Amount ({Balance.get_unit(0)})",
        justify="center",
        style=COLOR_PALETTE["POOLS"]["TAO"],
    )
    table.add_column(
        f"Rate (per {Balance.get_unit(0)})",
        justify="center",
        style=COLOR_PALETTE["POOLS"]["RATE"],
    )
    table.add_column(
        "Received",
        justify="center",
        style=COLOR_PALETTE["POOLS"]["TAO_EQUIV"],
    )
    table.add_column(
        "Fee (τ)",
        justify="center",
        style=COLOR_PALETTE["STAKE"]["STAKE_AMOUNT"],
    )

    if safe_staking:
        table.add_column(
            f"Rate with tolerance: [blue]({rate_tolerance * 100}%)[/blue]",
            justify="center",
            style=COLOR_PALETTE["POOLS"]["RATE"],
        )
        table.add_column(
            "Partial stake enabled",
            justify="center",
            style=COLOR_PALETTE["STAKE"]["SLIPPAGE_PERCENT"],
        )
    return table


def _print_table_and_slippage(table: Table, max_slippage: float, safe_staking: bool):
    console.print(table)

    if max_slippage > 5:
        message = (
            f"[{COLOR_PALETTE['STAKE']['SLIPPAGE_TEXT']}]" + ("-" * 115) + "\n"
            f"[bold]WARNING:[/bold]  The slippage on one of your operations is high: "
            f"[{COLOR_PALETTE['STAKE']['SLIPPAGE_PERCENT']}]{max_slippage} %[/{COLOR_PALETTE['STAKE']['SLIPPAGE_PERCENT']}], "
            f"this may result in a loss of funds.\n" + ("-" * 115) + "\n"
        )
        console.print(message)

    base_description = """
[bold white]Description[/bold white]:
The table displays information about the stake operation you are about to perform.
The columns are as follows:
    - [bold white]Netuid[/bold white]: The netuid of the subnet you are staking to.
    - [bold white]Hotkey[/bold white]: The ss58 address of the hotkey you are staking to.
    - [bold white]Amount[/bold white]: The TAO you are staking into this subnet onto this hotkey.
    - [bold white]Rate[/bold white]: The rate of exchange between your TAO and the subnet's stake.
    - [bold white]Received[/bold white]: The amount of stake you will receive on this subnet after slippage."""

    safe_staking_description = """
    - [bold white]Rate Tolerance[/bold white]: Maximum acceptable alpha rate. If the rate exceeds this tolerance, the transaction will be limited or rejected.
    - [bold white]Partial staking[/bold white]: If True, allows staking up to the rate tolerance limit. If False, the entire transaction will fail if rate tolerance is exceeded.\n"""

    console.print(base_description + (safe_staking_description if safe_staking else ""))


def add_command(
    wallet_name: str = typer.Option(
        ...,
        "--wallet-name",
        "--name",
        "--wallet_name",
        "--wallet.name",
        help="Name of the wallet to use"
    ),
    wallet_path: str = typer.Option(
        "~/.bittensor/wallets",
        "--wallet-path",
        "--path",
        "--wallet_path",
        "--wallet.path",
        help="Path to wallets directory"
    ),
    hotkey: Optional[str] = typer.Option(
        None,
        "--hotkey",
        "--wallet.hotkey",
        help="Hotkey name to use for staking"
    ),
    network: str = typer.Option(
        "finney",
        "--network",
        "--subtensor.network",
        help="Bittensor network to connect to"
    ),
    amount: Optional[float] = typer.Option(
        None,
        "--amount",
        help="Amount of TAO to stake"
    ),
    stake_all: bool = typer.Option(
        False,
        "--stake-all",
        help="Stake all available balance"
    ),
    all_hotkeys: bool = typer.Option(
        False,
        "--all-hotkeys",
        help="Stake to all hotkeys in the wallet"
    ),
    include_hotkeys: Optional[List[str]] = typer.Option(
        None,
        "--include-hotkeys",
        help="List of hotkeys to include"
    ),
    exclude_hotkeys: Optional[List[str]] = typer.Option(
        None,
        "--exclude-hotkeys",
        help="List of hotkeys to exclude"
    ),
    safe_staking: bool = typer.Option(
        False,
        "--safe-staking",
        help="Use safe staking with price tolerance"
    ),
    rate_tolerance: float = typer.Option(
        0.05,
        "--rate-tolerance",
        help="Rate tolerance percentage for safe staking"
    ),
    allow_partial_stake: bool = typer.Option(
        False,
        "--allow-partial-stake",
        help="Allow partial stake if rate tolerance is exceeded"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format"
    ),
    era: int = typer.Option(
        64,
        "--era",
        help="Blocks for which the transaction should be valid"
    ),
    prompt: bool = typer.Option(
        True,
        "--prompt/--no-prompt",
        help="Prompt for confirmation before staking"
    ),
):
    """Add stake to hotkeys on specified subnets"""

    # Create wallet object
    wallet = Wallet(
        name=wallet_name,
        path=wallet_path,
        hotkey=hotkey
    )

    # Run the async stake add function
    result = asyncio.run(stake_add(
        wallet=wallet,
        network=network,
        stake_all=stake_all,
        amount=amount,
        prompt=prompt,
        all_hotkeys=all_hotkeys,
        include_hotkeys=include_hotkeys or [],
        exclude_hotkeys=exclude_hotkeys or [],
        safe_staking=safe_staking,
        rate_tolerance=rate_tolerance,
        allow_partial_stake=allow_partial_stake,
        json_output=json_output,
        era=era,
    ))

    if not result:
        raise typer.Exit(code=1)
