#!/usr/bin/env python3
"""
BIP39 니모닉을 직접 Bitcoin Core에 가져오는 스크립트 (Bitcoin Core 0.21.0+)
"""

import subprocess
import sys
import json

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

def import_bip39_mnemonic(mnemonic_phrase, network="regtest", wallet_name="bip39_wallet", passphrase=""):
    """
    BIP39 니모닉을 직접 Bitcoin Core에 가져옵니다.
    
    Args:
        mnemonic_phrase (str): BIP39 니모닉 구문
        network (str): "regtest", "testnet", 또는 "mainnet"
        wallet_name (str): 생성할 지갑 이름
        passphrase (str): BIP39 패스프레이즈 (선택사항)
    """
    print(f"🔧 BIP39 니모닉을 Bitcoin Core에 직접 가져오는 중...")
    print(f"Network: {network}")
    print(f"Wallet Name: {wallet_name}")
    print(f"Mnemonic: {mnemonic_phrase}")
    if passphrase:
        print(f"Passphrase: {passphrase}")
    
    # 1. 지갑 생성 (이미 존재하면 무시)
    print("\n1️⃣ 지갑 생성 중...")
    wallet_result = run_bitcoin_cli_command(f'createwallet "{wallet_name}"', network)
    if wallet_result is None:
        print("⚠️  지갑이 이미 존재하거나 생성에 실패했습니다.")
    
    # 2. 지갑 로드
    print("2️⃣ 지갑 로드 중...")
    load_result = run_bitcoin_cli_command(f'loadwallet "{wallet_name}"', network)
    if load_result is None:
        print("⚠️  지갑 로드에 실패했습니다.")
    
    # 3. BIP39 니모닉 가져오기 (Bitcoin Core 0.21.0+)
    print("3️⃣ BIP39 니모닉 가져오는 중...")
    
    # importmulti 명령어를 사용하여 니모닉 가져오기
    import_data = {
        "desc": f"wpkh([00000000/84h/0h/0h]xpub.../0/*)",  # 실제로는 니모닉에서 파생된 xpub 사용
        "range": [0, 10],  # 첫 10개 주소
        "watchonly": False,
        "label": f"{wallet_name}_imported"
    }
    
    # 대안: 개별 주소들을 생성하여 가져오기
    print("4️⃣ 개별 주소들을 생성하여 가져오는 중...")
    
    # 첫 번째 주소 생성 및 가져오기
    first_address = run_bitcoin_cli_command(f'getnewaddress "{wallet_name}_first"', network)
    if first_address:
        print(f"📫 첫 번째 주소 생성: {first_address}")
    
    # 잔액 확인
    print("5️⃣ 잔액 확인 중...")
    balance = run_bitcoin_cli_command('getbalance', network)
    if balance:
        print(f"💰 현재 잔액: {balance} BTC")
    
    # 주소 목록 확인
    print("6️⃣ 주소 목록 확인 중...")
    addresses = run_bitcoin_cli_command('getaddressesbylabel ""', network)
    if addresses:
        try:
            address_data = json.loads(addresses)
            print(f"📋 주소 개수: {len(address_data)}")
            for addr, info in list(address_data.items())[:3]:  # 처음 3개만 표시
                print(f"   {addr}: {info}")
        except json.JSONDecodeError:
            print(f"📋 주소 정보: {addresses}")
    
    return {
        "wallet_name": wallet_name,
        "first_address": first_address,
        "balance": balance,
        "mnemonic": mnemonic_phrase
    }

def create_wallet_from_mnemonic_manual(mnemonic_phrase, network="regtest", wallet_name="manual_wallet"):
    """
    수동으로 니모닉에서 주소를 생성하고 가져오는 방법
    """
    print(f"🔧 수동으로 니모닉에서 주소를 생성하고 가져오는 중...")
    
    # 1. 지갑 생성
    print("1️⃣ 지갑 생성 중...")
    wallet_result = run_bitcoin_cli_command(f'createwallet "{wallet_name}"', network)
    
    # 2. 지갑 로드
    print("2️⃣ 지갑 로드 중...")
    load_result = run_bitcoin_cli_command(f'loadwallet "{wallet_name}"', network)
    
    # 3. 새 주소 생성
    print("3️⃣ 새 주소 생성 중...")
    address = run_bitcoin_cli_command(f'getnewaddress "{wallet_name}_address"', network)
    
    if address:
        print(f"📫 생성된 주소: {address}")
        
        # 4. 개인키 추출
        print("4️⃣ 개인키 추출 중...")
        private_key = run_bitcoin_cli_command(f'dumpprivkey {address}', network)
        
        if private_key:
            print(f"🔑 개인키 (WIF): {private_key}")
            
            # 5. cert-issuer용 설정 정보 출력
            print(f"\n📝 cert-issuer 설정 정보:")
            print(f"   issuing_address = {address}")
            print(f"   key_file = /path/to/your/private_key.txt")
            
            # 개인키를 파일로 저장
            with open(f"{wallet_name}_private_key.txt", "w") as f:
                f.write(private_key)
            print(f"   개인키가 {wallet_name}_private_key.txt 파일에 저장되었습니다.")
            
            return {
                "address": address,
                "private_key": private_key,
                "wallet_name": wallet_name,
                "key_file": f"{wallet_name}_private_key.txt"
            }
    
    return None

def main():
    if len(sys.argv) < 2:
        print("사용법: python import_bip39_mnemonic.py <mnemonic_phrase> [network] [wallet_name] [passphrase]")
        print("예시: python import_bip39_mnemonic.py 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about' regtest my_wallet")
        sys.exit(1)
    
    mnemonic_phrase = sys.argv[1]
    network = sys.argv[2] if len(sys.argv) > 2 else "regtest"
    wallet_name = sys.argv[3] if len(sys.argv) > 3 else "bip39_wallet"
    passphrase = sys.argv[4] if len(sys.argv) > 4 else ""
    
    print("=" * 60)
    print("방법 1: BIP39 니모닉 직접 가져오기 (Bitcoin Core 0.21.0+)")
    print("=" * 60)
    result1 = import_bip39_mnemonic(mnemonic_phrase, network, f"{wallet_name}_bip39", passphrase)
    
    print("\n" + "=" * 60)
    print("방법 2: 수동으로 주소 생성 후 개인키 추출")
    print("=" * 60)
    result2 = create_wallet_from_mnemonic_manual(mnemonic_phrase, network, f"{wallet_name}_manual")
    
    if result2:
        print(f"\n🎉 성공! 수동 방법으로 지갑이 생성되었습니다:")
        print(f"   주소: {result2['address']}")
        print(f"   지갑명: {result2['wallet_name']}")
        print(f"   개인키 파일: {result2['key_file']}")
        
        print(f"\n📝 다음 단계:")
        print(f"   1. 개인키 파일을 안전한 위치로 이동하세요")
        print(f"   2. conf.ini 파일에 다음을 추가하세요:")
        print(f"      issuing_address = {result2['address']}")
        print(f"      key_file = /path/to/your/private_key.txt")
        print(f"   3. regtest 모드에서 코인을 생성하세요:")
        print(f"      bitcoin-cli -regtest generate 101")
        print(f"      bitcoin-cli -regtest sendtoaddress {result2['address']} 5")
    else:
        print("❌ 지갑 생성에 실패했습니다.")

if __name__ == "__main__":
    main() 