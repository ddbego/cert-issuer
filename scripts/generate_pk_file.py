#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import BitcoinMainnet
import json

def generate_private_keys():
    # Initialize HDWallet with Bitcoin cryptocurrency
    hdwallet = HDWallet(cryptocurrency=BitcoinMainnet)
    
    # Generate a new HD wallet with random mnemonic
    hdwallet.from_mnemonic(
        mnemonic="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    )
    
    # Derive the first account (m/44'/0'/0'/0/0)
    hdwallet.from_path("m/44'/0'/0'/0/0")
    
    # Get the private key
    private_key = hdwallet.private_key()
    
    # Get the public key and address
    public_key = hdwallet.public_key()
    address = hdwallet.address()
    
    # Create output dictionary
    wallet_info = {
        "private_key": private_key,
        "public_key": public_key,
        "address": address,
        "path": hdwallet.path(),
        "mnemonic": hdwallet.mnemonic()
    }
    
    # Save to file
    with open("wallet_keys.json", "w") as f:
        json.dump(wallet_info, f, indent=2)
    
    print("Wallet information saved to wallet_keys.json")
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")
    
    return wallet_info

if __name__ == "__main__":
    try:
        wallet_info = generate_private_keys()
        print("Successfully generated wallet keys!")
    except Exception as e:
        print(f"Error: {e}") 