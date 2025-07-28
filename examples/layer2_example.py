#!/usr/bin/env python3
"""
Example: Issuing digital credentials on Layer2 networks
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cert_issuer import config
from cert_issuer.issue_certificates import main as issue_certificates

def create_sample_certificate():
    """Create a sample verifiable credential"""
    certificate = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1"
        ],
        "id": "urn:uuid:12345678-1234-1234-1234-123456789abc",
        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
        "issuer": {
            "id": "did:example:123456789abcdefghi",
            "name": "Example University"
        },
        "issuanceDate": "2024-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:abcdef123456789",
            "name": "John Doe",
            "degree": {
                "type": "BachelorDegree",
                "name": "Bachelor of Science in Computer Science"
            },
            "university": "Example University"
        }
    }
    return certificate

def setup_directories():
    """Setup necessary directories for certificate issuance"""
    base_dir = Path("data-testnet")
    
    # Create directories
    directories = [
        base_dir / "unsigned_certificates",
        base_dir / "blockchain_certificates",
        base_dir / "work",
        Path("issuer")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_config_file(network="polygon_mumbai"):
    """Create a configuration file for Layer2 network"""
    config_content = f"""[ISSUER]
# Layer2 Network Configuration
chain={network}
issuing_address=<your-wallet-address>
revocation_address=<your-wallet-address>
key_file=issuer/key.txt

# API tokens (get from respective block explorers)
polygonscan_api_token=<your-polygonscan-api-token>
arbiscan_api_token=<your-arbiscan-api-token>
optimistic_etherscan_api_token=<your-optimistic-etherscan-api-token>

# RPC URLs (optional)
polygon_rpc_url=https://polygon-rpc.com
mumbai_rpc_url=https://rpc-mumbai.maticvigil.com
arbitrum_rpc_url=https://arb1.arbitrum.io/rpc
arbitrum_goerli_rpc_url=https://goerli-rollup.arbitrum.io/rpc
optimism_rpc_url=https://mainnet.optimism.io
optimism_goerli_rpc_url=https://goerli.optimism.io

# Gas settings (adjust based on network)
gas_price=30000000000
gas_limit=25000
max_priority_fee_per_gas=0
gas_price_dynamic=false

# Certificate settings
batch_size=1
safe_mode=true

# File paths
unsigned_certificates_dir=data-testnet/unsigned_certificates
blockchain_certificates_dir=data-testnet/blockchain_certificates
work_dir=data-testnet/work
"""
    
    with open("conf_layer2_example.ini", "w") as f:
        f.write(config_content)
    
    print("Created configuration file: conf_layer2_example.ini")

def create_sample_certificates():
    """Create sample certificates for testing"""
    certificate = create_sample_certificate()
    
    # Create multiple certificates with different IDs
    for i in range(3):
        cert_copy = certificate.copy()
        cert_copy["id"] = f"urn:uuid:12345678-1234-1234-1234-{i:012d}"
        cert_copy["credentialSubject"]["name"] = f"Student {i+1}"
        
        filename = f"data-testnet/unsigned_certificates/certificate_{i+1}.json"
        with open(filename, "w") as f:
            json.dump(cert_copy, f, indent=2)
        
        print(f"Created certificate: {filename}")

def print_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("LAYER2 DIGITAL CREDENTIAL ISSUANCE SETUP")
    print("="*60)
    
    print("\n1. SETUP REQUIREMENTS:")
    print("   - Get API tokens from block explorers:")
    print("     * Polygonscan: https://polygonscan.com/apis")
    print("     * Arbiscan: https://arbiscan.io/apis")
    print("     * Optimistic Etherscan: https://optimistic.etherscan.io/apis")
    
    print("\n2. GET TEST TOKENS:")
    print("   - Polygon Mumbai: https://faucet.polygon.technology/")
    print("   - Arbitrum Goerli: https://goerlifaucet.com/")
    print("   - Optimism Goerli: https://optimism.io/faucet")
    
    print("\n3. CONFIGURE:")
    print("   - Edit conf_layer2_example.ini with your details")
    print("   - Add your wallet address and API tokens")
    print("   - Create your private key file at issuer/key.txt")
    
    print("\n4. ISSUE CERTIFICATES:")
    print("   python -m cert_issuer -c conf_layer2_example.ini")
    
    print("\n5. VERIFY:")
    print("   - Check the generated certificates in data-testnet/blockchain_certificates/")
    print("   - View transactions on respective block explorers")
    
    print("\n" + "="*60)

def main():
    """Main function to setup Layer2 certificate issuance"""
    print("Setting up Layer2 digital credential issuance...")
    
    # Setup directories
    setup_directories()
    
    # Create configuration file
    create_config_file()
    
    # Create sample certificates
    create_sample_certificates()
    
    # Print instructions
    print_instructions()
    
    print("\nSetup complete! Follow the instructions above to issue certificates.")

if __name__ == "__main__":
    main() 