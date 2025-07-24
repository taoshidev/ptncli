![Screenshot](assets/ptncli.png)

<div align="center">

## Revolutionizing Financial Market Trading

</div>

**PTNCLI** is a command-line tool that extends the bittensor-cli tool for Proprietary Trading Network (PTN) operations. It provides enhanced registration functionality with collateral management and extends standard Bittensor wallet, subnet, and stake operations.

## Note

PTNCLI is in beta and is still under active development. Please report any issues or feedback on the [PTNCLI GitHub repository](https://github.com/proprietary-trading-network/ptncli).

## Description

PTNCLI sits on top of the bittensor-cli tool and extends it by customizing and hooking into commands. As a subnet on the Bittensor network, PTN operates on **subnet 8 (netuid: 8)** on the mainnet/finney network and **subnet 116 (netuid: 116)** on the testnet. PTN requires additional collateral setup during registration, which this tool automates alongside the standard subnet registration process.

### Process Flow
From a high level, here is what happens to register with collateral on PTN.

1. Register your hotkey with PTN: `ptncli subnets register`
2. Stake TAO into theta using your own hotkey: `ptncli stake add`
3. Collateral add, which under the hood signs an extensic and sends the command off to the super validator. The super validator will then transfer the amount specified into our smart contract: `ptncli collateral add`
4. (Optional) View collateral amount tracked in the contract: `ptncli collateral list`


### Network Targeting
- **Mainnet/Finney**: Targets subnet 8 (netuid: 8)
- **Testnet**: Targets subnet 116 (netuid: 116)
- Commands automatically select the correct subnet based on the network parameter

## Installation

### From Source
```bash
git clone <repository-url>
cd ptncli
pip install .
```
### Homebrew (macOS/Linux)
Coming soon

### Pip
Coming soon

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
- `--wallet.hotkey, --hotkey` - Name of the hotkey to use
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

#### Register to Subnet 8
```bash
ptncli subnets register [OPTIONS]
```
Registers a neuron to the Proprietary Trading Network with automatic collateral setup. Automatically targets:
- **Subnet 8 (netuid: 8)** on mainnet/finney
- **Subnet 116 (netuid: 116)** on testnet

**Options:**
- `--wallet-name, --name` - Name of the wallet to use for registration
- `--wallet.hotkey, --hotkey` - Name of the hotkey to use
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
Add stake to hotkeys on the Proprietary Trading Network. Automatically targets:
- **Subnet 8 (netuid: 8)** on mainnet/finney
- **Subnet 116 (netuid: 116)** on testnet

**Options:**
- `--wallet-name, --name` - Name of the wallet to use (required)
- `--wallet.hotkey, --hotkey` - Hotkey name to use for staking
- `--wallet-path, --path` - Path to wallets directory (default: `~/.bittensor/wallets`)
- `--network` - Network to connect to (default: `finney`)
- `--amount` - Amount of TAO to stake

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

### Collateral Operations

#### Add Collateral
```bash
ptncli collateral add [OPTIONS]
```
Add collateral to the Proprietary Trading Network.

**Options:**
- `--wallet-name, --name` - Name of the wallet to use for collateral (required)
- `--wallet-path` - Path to the wallet directory (default: `~/.bittensor/wallets`)
- `--network` - Network to connect to (default: `test`)
- `--amount` - Amount of TAO to use for collateral (default: 1)

#### List Collateral Balance
```bash
ptncli collateral list [OPTIONS]
```
Check collateral balance for a miner address.

**Options:**
- `--miner-address, --miner_address` - Miner SS58 address to check collateral balance for (required)
- `--wallet-name, --name` - Name of the wallet (for display purposes)
- `--wallet.hotkey, --hotkey` - Name of the hotkey to use
- `--json` - Output result as JSON

#### Withdraw Collateral
```bash
ptncli collateral withdraw [OPTIONS]
```
Withdraw collateral from the Proprietary Trading Network.

**Options:**
- `--amount` - Amount to withdraw from collateral (required)
- `--miner-address, --miner_address` - Miner SS58 address to withdraw collateral for (required)
- `--wallet-name, --name` - Name of the wallet (for display purposes)
- `--wallet.hotkey, --hotkey` - Name of the hotkey to use
- `--wallet-path` - Path to wallet directory (default: `~/.bittensor/wallets`)
- `--prompt/--no-prompt` - Whether to prompt for confirmation

## Examples

### Register to PTN with collateral
```bash
# Register on testnet (targets subnet 116)
ptncli subnets register --wallet-name my_wallet --hotkey my_hotkey --network test

# Register on mainnet (targets subnet 8)
ptncli subnets register --wallet-name my_wallet --hotkey my_hotkey --network finney
```

### List wallet stakes with live monitoring
```bash
# List stakes on mainnet
ptncli stake list --wallet-name my_wallet --live --network finney

# List stakes on testnet
ptncli stake list --wallet-name my_wallet --live --network test
```

### Add stake to all hotkeys
```bash
# Add stake on mainnet (subnet 8)
ptncli stake add --wallet-name my_wallet --all-hotkeys --amount 10.0 --network finney

# Add stake on testnet (subnet 116)
ptncli stake add --wallet-name my_wallet --all-hotkeys --amount 10.0 --network test
```

### View wallet overview
```bash
ptncli wallet overview --wallet-name my_wallet --network finney
```

### Add collateral
```bash
# Add collateral on testnet
ptncli collateral add --wallet-name my_wallet --amount 1.0 --network test

# Add collateral on mainnet
ptncli collateral add --wallet-name my_wallet --amount 1.0 --network finney
```

### Check collateral balance
```bash
ptncli collateral list --miner-address 5HE... --wallet-name my_wallet
```

### Withdraw collateral
```bash
ptncli collateral withdraw --amount 5.0 --miner-address 5HE... --wallet-name my_wallet
```

## Requirements

- Python >= 3.13, < 3.14
- bittensor-cli >= 9.7.1
- Access to Bittensor network

## License

MIT License
