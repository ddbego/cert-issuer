# Layer2 Configuration Guide

This guide explains how to configure cert-issuer to work with Layer2 scaling solutions for issuing digital credentials with lower costs and faster processing.

## Supported Layer2 Networks

### Polygon (MATIC)
- **Mainnet**: `polygon_mainnet`
- **Testnet**: `polygon_mumbai`
- **Chain ID**: 137 (mainnet), 80001 (testnet)
- **Block Explorer**: [Polygonscan](https://polygonscan.com)
- **RPC Endpoints**: 
  - Mainnet: `https://polygon-rpc.com`
  - Testnet: `https://rpc-mumbai.maticvigil.com`

### Arbitrum One
- **Mainnet**: `arbitrum_one`
- **Testnet**: `arbitrum_goerli`
- **Chain ID**: 42161 (mainnet), 421613 (testnet)
- **Block Explorer**: [Arbiscan](https://arbiscan.io)
- **RPC Endpoints**:
  - Mainnet: `https://arb1.arbitrum.io/rpc`
  - Testnet: `https://goerli-rollup.arbitrum.io/rpc`

### Optimism
- **Mainnet**: `optimism_mainnet`
- **Testnet**: `optimism_goerli`
- **Chain ID**: 10 (mainnet), 420 (testnet)
- **Block Explorer**: [Optimistic Etherscan](https://optimistic.etherscan.io)
- **RPC Endpoints**:
  - Mainnet: `https://mainnet.optimism.io`
  - Testnet: `https://goerli.optimism.io`

## Configuration Setup

### 1. API Tokens

You'll need API tokens from the respective block explorers:

- **Polygonscan**: Get from [Polygonscan API](https://polygonscan.com/apis)
- **Arbiscan**: Get from [Arbiscan API](https://arbiscan.io/apis)
- **Optimistic Etherscan**: Get from [Optimistic Etherscan API](https://optimistic.etherscan.io/apis)

### 2. Configuration File

Create a configuration file based on `conf_layer2.ini`:

```ini
[ISSUER]
# Choose your Layer2 network
chain=polygon_mainnet

# Your wallet address
issuing_address=<your-wallet-address>
revocation_address=<your-wallet-address>

# Private key file
key_file=issuer/key.txt

# API tokens
polygonscan_api_token=<your-polygonscan-api-token>
arbiscan_api_token=<your-arbiscan-api-token>
optimistic_etherscan_api_token=<your-optimistic-etherscan-api-token>

# RPC URLs (optional)
polygon_rpc_url=https://polygon-rpc.com
arbitrum_rpc_url=https://arb1.arbitrum.io/rpc
optimism_rpc_url=https://mainnet.optimism.io

# Gas settings
gas_price=30000000000
gas_limit=25000
max_priority_fee_per_gas=0
gas_price_dynamic=false

# Certificate settings
batch_size=10
safe_mode=true

# File paths
unsigned_certificates_dir=data-testnet/unsigned_certificates
blockchain_certificates_dir=data-testnet/blockchain_certificates
work_dir=data-testnet/work
```

### 3. Network-Specific Configuration

#### Polygon Configuration
```ini
chain=polygon_mainnet
polygonscan_api_token=<your-api-token>
polygon_rpc_url=https://polygon-rpc.com
gas_price=30000000000
```

#### Arbitrum Configuration
```ini
chain=arbitrum_one
arbiscan_api_token=<your-api-token>
arbitrum_rpc_url=https://arb1.arbitrum.io/rpc
gas_price=1000000000
```

#### Optimism Configuration
```ini
chain=optimism_mainnet
optimistic_etherscan_api_token=<your-api-token>
optimism_rpc_url=https://mainnet.optimism.io
gas_price=1000000
```

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Test Tokens
For testnets, you'll need test tokens:
- **Polygon Mumbai**: Get MATIC from [Polygon Faucet](https://faucet.polygon.technology/)
- **Arbitrum Goerli**: Get ETH from [Arbitrum Faucet](https://goerlifaucet.com/)
- **Optimism Goerli**: Get ETH from [Optimism Faucet](https://optimism.io/faucet)

### 3. Issue Certificates
```bash
python -m cert_issuer -c conf_layer2.ini
```

## Gas Optimization

Layer2 networks have different gas characteristics:

### Polygon
- Uses MATIC for gas fees
- Generally lower gas prices than Ethereum
- Recommended gas price: 30 Gwei

### Arbitrum
- Uses ETH for gas fees
- Very low gas prices due to optimistic rollups
- Recommended gas price: 1 Gwei

### Optimism
- Uses ETH for gas fees
- Low gas prices due to optimistic rollups
- Recommended gas price: 0.001 Gwei

## Benefits of Layer2

### Cost Savings
- **Polygon**: ~100x cheaper than Ethereum
- **Arbitrum**: ~10-100x cheaper than Ethereum
- **Optimism**: ~10-100x cheaper than Ethereum

### Speed
- **Polygon**: ~2 second block time
- **Arbitrum**: ~1 second block time
- **Optimism**: ~2 second block time

### Security
- All Layer2 solutions inherit security from Ethereum
- Polygon uses Plasma and PoS
- Arbitrum and Optimism use optimistic rollups

## Troubleshooting

### Common Issues

1. **Insufficient Balance**: Make sure your wallet has enough tokens for gas fees
2. **API Rate Limits**: Consider using RPC endpoints for high-volume operations
3. **Network Congestion**: Adjust gas prices during high network usage

### Error Messages

- `Polygonscan broadcast failed`: Check your API token and network connectivity
- `Failed to get balance`: Verify your wallet address and network configuration
- `Transaction signing failed`: Ensure your private key file is correct

## Best Practices

1. **Start with Testnets**: Always test on testnets before mainnet
2. **Monitor Gas Prices**: Use dynamic gas pricing for optimal costs
3. **Batch Operations**: Use appropriate batch sizes for your use case
4. **Backup Keys**: Keep your private keys secure and backed up
5. **Monitor Transactions**: Use block explorers to track your transactions

## Example Transaction IDs

### Polygon Mainnet
- Example: `0x1234567890abcdef...`
- Explorer: https://polygonscan.com/tx/0x1234567890abcdef...

### Arbitrum One
- Example: `0xabcdef1234567890...`
- Explorer: https://arbiscan.io/tx/0xabcdef1234567890...

### Optimism Mainnet
- Example: `0x7890abcdef123456...`
- Explorer: https://optimistic.etherscan.io/tx/0x7890abcdef123456... 