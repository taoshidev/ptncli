![Screenshot](assets/ptncli.png)

<div align="center">

## Revolutionizing Financial Market Trading

</div>

**PTNCLI** is a command-line tool that extends the bittensor-cli tool for Proprietary Trading Network (PTN) operations. It provides enhanced registration functionality with collateral management and extends standard Bittensor wallet, subnet, and stake operations.

## Description

PTNCLI sits on top of the bittensor-cli tool and extends it by customizing and hooking into commands. As a subnet on the Bittensor network, PTN requires additional collateral setup during registration, which this tool automates alongside the standard subnet registration process.

## Installation

### Homebrew (macOS/Linux)
```bash
brew install ptncli
```

### Pip
```bash
pip install ptncli
```

### From Source
```bash
git clone <repository-url>
cd ptncli
pip install .
```

## Commands

All commands are prefixed with `ptncli`. For example: `ptncli wallet list`

### Wallet Operations

#### List Wallets
```bash
ptncli wallet list [OPTIONS]
```
Lists all available wallets with registration information.

**Options:**
- `--wallet-path, --path` - Path to wallets directory (default: `~/.bittensor/wallets`)

#### Wallet Overview
```bash
ptncli wallet overview [OPTIONS]
```
Shows detailed wallet information including balance and registration status.

**Options:**
- `--wallet-name, --name` - Name of the wallet
- `--wallet-path, --path` - Path to wallets directory (default: `~/.bittensor/wallets`)
- `--network` - Network to connect to (default: `finney`)
- `--json` - Output result as JSON

#### Create New Coldkey
```bash
ptncli wallet new_coldkey [OPTIONS]
```
Creates a new coldkey for the wallet.

#### Create New Hotkey
```bash
ptncli wallet new_hotkey [OPTIONS]
```
Creates a new hotkey for the wallet.

### Subnet Operations

#### List Subnets
```bash
ptncli subnets list [OPTIONS]
```
Lists all available subnets with detailed information.

**Options:**
- `--network` - Network to connect to (default: `finney`)
- `--verbose` - Enable verbose output
- `--live` - Display live view of the table
- `--json` - Output result as JSON

#### Register to Subnet
```bash
ptncli subnets register [OPTIONS]
```
Registers a neuron to the Proprietary Trading Network (subnet 8 on mainnet, subnet 116 on testnet) with automatic collateral setup.

**Options:**
- `--wallet-name, --name` - Name of the wallet to use for registration
- `--wallet-hotkey, --hotkey` - Name of the hotkey to use
- `--wallet-path` - Path to wallet directory (default: `~/.bittensor/wallets`)
- `--network` - Network to connect to (default: `test`)
- `--era` - Era to register for
- `--json` - Output result as JSON
- `--prompt/--no-prompt` - Whether to prompt for confirmation

### Stake Operations

#### Add Stake
```bash
ptncli stake add [OPTIONS]
```
Add stake to hotkeys on the Proprietary Trading Network.

**Options:**
- `--wallet-name, --name` - Name of the wallet to use (required)
- `--wallet-path, --path` - Path to wallets directory (default: `~/.bittensor/wallets`)
- `--hotkey` - Hotkey name to use for staking
- `--network` - Network to connect to (default: `finney`)
- `--amount` - Amount of TAO to stake
- `--stake-all` - Stake all available balance
- `--all-hotkeys` - Stake to all hotkeys in the wallet
- `--include-hotkeys` - List of hotkeys to include
- `--exclude-hotkeys` - List of hotkeys to exclude
- `--safe-staking` - Use safe staking with price tolerance
- `--rate-tolerance` - Rate tolerance percentage (default: 0.05)
- `--allow-partial-stake` - Allow partial stake if rate tolerance exceeded
- `--era` - Blocks for transaction validity (default: 64)
- `--json` - Output results in JSON format
- `--prompt/--no-prompt` - Whether to prompt for confirmation

#### List Stakes
```bash
ptncli stake list [OPTIONS]
```
Lists stakes for a wallet with detailed information.

**Options:**
- `--wallet-name, --name` - Name of the wallet to list stakes for
- `--wallet-path` - Path to wallet directory (default: `~/.bittensor/wallets`)
- `--network` - Network to connect to (default: `test`)
- `--coldkey_ss58` - Coldkey SS58 address to list stakes for
- `--live` - Enable live monitoring of stakes
- `--verbose` - Enable verbose output
- `--json` - Output result as JSON
- `--prompt/--no-prompt` - Whether to prompt for confirmation

## Examples

### Register to PTN with collateral
```bash
ptncli subnets register --wallet-name my_wallet --hotkey my_hotkey --network test
```

### List wallet stakes with live monitoring
```bash
ptncli stake list --wallet-name my_wallet --live --network finney
```

### Add stake to all hotkeys
```bash
ptncli stake add --wallet-name my_wallet --all-hotkeys --amount 10.0 --network finney
```

### View wallet overview
```bash
ptncli wallet overview --wallet-name my_wallet --network finney
```

## Requirements

- Python >= 3.13, < 3.14
- bittensor-cli >= 9.7.1
- Access to Bittensor network

## License

MIT License
