#!/usr/bin/env python3
"""
니모닉을 사용하여 Bitcoin Core 지갑에 개인키를 가져오는 스크립트
"""

import subprocess
import sys
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import BitcoinMainnet, BitcoinTestnet

def run_bitcoin_cli_command(command, network="regtest"):
    """bitcoin-cli 명령어 실행"""
    try:
        if network == "regtest":
            result = subprocess.run(['bitcoin-cli', '-regtest'] + command.split(), 
                                  capture_output=True, text=True, check=True)
        elif network == "testnet":
            result = subprocess.run(['bitcoin-cli', '-testnet'] + command.split(), 
                                  capture_output=True, text=True, check=True)
        else:  # mainnet
            result = subprocess.run(['bitcoin-cli'] + command.split(), 
                                  capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running bitcoin-cli command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def import_mnemonic_to_bitcoin(mnemonic_phrase, network="regtest", wallet_name="mnemonic_wallet"):
    """
    니모닉을 사용하여 Bitcoin Core 지갑에 개인키를 가져옵니다.
    
    Args:
        mnemonic_phrase (str): BIP39 니모닉 구문
        network (str): "regtest", "testnet", 또는 "mainnet"
        wallet_name (str): 생성할 지갑 이름
    """
    print(f"🔧 니모닉을 사용하여 Bitcoin Core 지갑에 개인키를 가져오는 중...")
    print(f"Network: {network}")
    print(f"Wallet Name: {wallet_name}")
    print(f"Mnemonic: {mnemonic_phrase}")
    
    # 네트워크에 따른 설정
    if network == "mainnet":
        path = "m/84'/0'/0'/0/0"  # Native SegWit (mainnet)
        cryptocurrency = BitcoinMainnet
    elif network == "testnet":
        path = "m/84'/1'/0'/0/0"  # Native SegWit (testnet)
        cryptocurrency = BitcoinTestnet
    elif network == "regtest":
        path = "m/44'/1'/0'/0/0"  # Legacy (regtest)
        cryptocurrency = BitcoinTestnet
    else:
        print(f"Unknown network: {network}. Using regtest as default.")
        path = "m/44'/1'/0'/0/0"
        cryptocurrency = BitcoinTestnet
        network = "regtest"
    
    # HDWallet 객체 생성
    hdwallet = HDWallet(cryptocurrency=cryptocurrency)
    hdwallet.from_mnemonic(mnemonic=mnemonic_phrase)
    hdwallet.from_path(path=path)
    
    # 개인키 (WIF 형식) 추출
    private_key_wif = hdwallet.wif()
    address = hdwallet.address()
    
    print(f"📫 Generated Address: {address}")
    print(f"🔑 Private Key (WIF): {private_key_wif}")
    
    # Bitcoin Core 지갑 생성 (이미 존재하면 무시)
    print("\n1️⃣ 지갑 생성 중...")
    wallet_result = run_bitcoin_cli_command(f'createwallet "{wallet_name}"', network)
    if wallet_result is None:
        print("⚠️  지갑이 이미 존재하거나 생성에 실패했습니다.")
    
    # 지갑 로드
    print("2️⃣ 지갑 로드 중...")
    load_result = run_bitcoin_cli_command(f'loadwallet "{wallet_name}"', network)
    if load_result is None:
        print("⚠️  지갑 로드에 실패했습니다.")
    
    # 개인키 가져오기
    print("3️⃣ 개인키 가져오는 중...")
    import_result = run_bitcoin_cli_command(f'importprivkey "{private_key_wif}" "{wallet_name}_key"', network)
    if import_result is None:
        print("❌ 개인키 가져오기에 실패했습니다.")
        return None
    
    print("✅ 개인키가 성공적으로 가져와졌습니다!")
    
    # 잔액 확인
    print("4️⃣ 잔액 확인 중...")
    balance = run_bitcoin_cli_command('getbalance', network)
    if balance:
        print(f"💰 현재 잔액: {balance} BTC")
    
    # 주소 목록 확인
    print("5️⃣ 주소 목록 확인 중...")
    addresses = run_bitcoin_cli_command('getaddressinfo', network)
    if addresses:
        print(f"📋 주소 정보: {addresses}")
    
    return {
        "address": address,
        "private_key": private_key_wif,
        "wallet_name": wallet_name,
        "balance": balance
    }

def main():
    if len(sys.argv) < 2:
        print("사용법: python import_mnemonic_to_bitcoin.py <mnemonic_phrase> [network] [wallet_name]")
        print("예시: python import_mnemonic_to_bitcoin.py 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about' regtest my_wallet")
        sys.exit(1)
    
    mnemonic_phrase = sys.argv[1]
    network = sys.argv[2] if len(sys.argv) > 2 else "regtest"
    wallet_name = sys.argv[3] if len(sys.argv) > 3 else "mnemonic_wallet"
    
    result = import_mnemonic_to_bitcoin(mnemonic_phrase, network, wallet_name)
    
    if result:
        print(f"\n🎉 성공! 지갑 정보:")
        print(f"   주소: {result['address']}")
        print(f"   지갑명: {result['wallet_name']}")
        print(f"   잔액: {result['balance']} BTC")
        
        # cert-issuer 설정 파일 업데이트 제안
        print(f"\n📝 cert-issuer 설정을 위해 다음을 conf.ini에 추가하세요:")
        print(f"   issuing_address = {result['address']}")
        print(f"   key_file = /path/to/your/private_key.txt")
    else:
        print("❌ 지갑 가져오기에 실패했습니다.")

if __name__ == "__main__":
    main() 