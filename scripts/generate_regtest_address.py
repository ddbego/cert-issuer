#!/usr/bin/env python3
"""
Generate Bitcoin addresses for regtest mode using bitcoin-cli.
This is the most reliable method for regtest addresses.
"""

import subprocess
import sys
import json

def run_bitcoin_cli_command(command):
    """Run a bitcoin-cli command and return the result"""
    try:
        result = subprocess.run(['bitcoin-cli', '-regtest'] + command.split(), 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running bitcoin-cli command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def generate_regtest_address():
    """Generate a new regtest address and its private key"""
    print("🔧 Generating regtest address using bitcoin-cli...")
    
    # Check if bitcoin-cli is available
    try:
        subprocess.run(['bitcoin-cli', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: bitcoin-cli not found. Make sure Bitcoin Core is installed and in your PATH.")
        return None
    
    # Check if bitcoind is running
    try:
        subprocess.run(['bitcoin-cli', '-regtest', 'getblockchaininfo'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Error: Cannot connect to bitcoind. Make sure bitcoind is running in regtest mode.")
        print("Start bitcoind with: bitcoind -regtest -daemon")
        return None
    
    # Generate new address
    address = run_bitcoin_cli_command('getnewaddress')
    if not address:
        print("❌ Failed to generate address")
        return None
    
    # Get private key for the address
    private_key = run_bitcoin_cli_command(f'dumpprivkey {address}')
    if not private_key:
        print("❌ Failed to get private key")
        return None
    
    # Get wallet info
    wallet_info = run_bitcoin_cli_command('getwalletinfo')
    
    print(f"\n✅ Successfully generated regtest address!")
    print(f"📫 Address: {address}")
    print(f"🔑 Private Key (WIF): {private_key}")
    
    if wallet_info:
        try:
            wallet_data = json.loads(wallet_info)
            print(f"💰 Wallet Balance: {wallet_data.get('balance', 'N/A')} BTC")
        except json.JSONDecodeError:
            pass
    
    print(f"\n📝 To fund this address in regtest mode:")
    print(f"   bitcoin-cli -regtest generate 101")
    print(f"   bitcoin-cli -regtest sendtoaddress {address} 5")
    
    return {
        'address': address,
        'private_key': private_key,
        'network': 'regtest'
    }

def main():
    """Main function"""
    print("🚀 Bitcoin Regtest Address Generator")
    print("=" * 40)
    
    result = generate_regtest_address()
    
    if result:
        print(f"\n💾 Save this information securely!")
        print(f"Address: {result['address']}")
        print(f"Private Key: {result['private_key']}")
    else:
        print("\n❌ Failed to generate address. Please check your Bitcoin Core setup.")
        sys.exit(1)

if __name__ == "__main__":
    main() 