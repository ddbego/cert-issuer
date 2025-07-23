import sys
import argparse
from pycoin.key import Key
from pycoin.key.BIP32Node import BIP32Node
import secrets
import os

def generate_new_key_pair():
    """
    Generate a new private key and corresponding address.
    Returns tuple of (wif_private_key, address)
    """
    private_key_bytes = secrets.token_bytes(32)
    key = Key(secret_exponent=int.from_bytes(private_key_bytes, byteorder='big'))
    return key.wif(), key.address()

def import_private_key(wif_private_key):
    """
    Import an existing WIF private key and get its address.
    Returns tuple of (wif_private_key, address)
    """
    try:
        key = Key.from_text(wif_private_key)
        return key.wif(), key.address()
    except Exception as e:
        raise ValueError(f"Invalid WIF private key: {e}")

def generate_key_from_seed(seed_phrase, derivation_path="m/44'/0'/0'/0/0"):
    """
    Generate a key from a seed phrase using BIP32 derivation.
    Returns tuple of (wif_private_key, address)
    """
    try:
        # Create BIP32 node from seed
        bip32_node = BIP32Node.from_master_secret(seed_phrase.encode('utf-8'))
        # Derive child key
        child_node = bip32_node.subkey_for_path(derivation_path)
        # Convert to regular key
        key = Key(secret_exponent=child_node.secret_exponent())
        return key.wif(), key.address()
    except Exception as e:
        raise ValueError(f"Error generating key from seed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate or import WIF private key file for Bitcoin addresses')
    parser.add_argument('--address', '-a', help='Target Bitcoin address (for verification)')
    parser.add_argument('--output', '-o', default='/etc/cert-issuer/pk_issuer.txt', 
                       help='Output file path for the WIF private key (default: /etc/cert-issuer/pk_issuer.txt)')
    parser.add_argument('--import-wif', '-i', help='Import existing WIF private key')
    parser.add_argument('--seed', '-s', help='Generate key from seed phrase')
    parser.add_argument('--derivation-path', default="m/44'/0'/0'/0/0", 
                       help='BIP32 derivation path (default: m/44\'/0\'/0\'/0/0)')
    parser.add_argument('--new', action='store_true', help='Generate new random key pair')
    
    args = parser.parse_args()      
       
    wif_private_key = None
    generated_address = None
    
    # Determine which method to use
    if args.import_wif:
        print("Importing existing WIF private key...")
        wif_private_key, generated_address = import_private_key(args.import_wif)
    elif args.seed:
        print("Generating key from seed phrase...")
        wif_private_key, generated_address = generate_key_from_seed(args.seed, args.derivation_path)
    elif args.new:
        print("Generating new random key pair...")
        wif_private_key, generated_address = generate_new_key_pair()
    else:
        print("No method specified. Generating new random key pair...")
        wif_private_key, generated_address = generate_new_key_pair()
    
    # Verify address if provided
    if args.address:
        if generated_address == args.address:
            print(f"✓ Generated address matches target address: {generated_address}")
        else:
            print(f"⚠ Warning: Generated address {generated_address} doesn't match target address {args.address}")
            print("Make sure you're using the correct method to generate the private key.")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to file
    with open(args.output, "w") as f:
        f.write(wif_private_key)
    
    print(f"Generated Address: {generated_address}")
    print(f"WIF Private Key: {wif_private_key}")
    print(f"WIF private key saved to {args.output}")

if __name__ == "__main__":
    main()