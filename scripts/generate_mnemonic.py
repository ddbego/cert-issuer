import sys
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from hdwallet.utils import generate_mnemonic
from hdwallet.cryptocurrencies import BitcoinMainnet, BitcoinTestnet

def generate_keys(network="regtest", existing_mnemonic=None):
    if existing_mnemonic:
        mnemonic_phrase = existing_mnemonic
        print(f"Using existing mnemonic: {mnemonic_phrase}")
    else:
        mnemonic_phrase = generate_mnemonic(language="english", strength=256)
        print(f"Generated new mnemonic: {mnemonic_phrase}")
        print("⚠️  IMPORTANT: Save this mnemonic phrase securely!")

    # 네트워크에 따른 파생 경로 설정
    if network == "mainnet":
        path = "m/84'/0'/0'/0/0"  # Native SegWit (mainnet)
        cryptocurrency = BitcoinMainnet
        print(f"Network: Mainnet")
    elif network == "testnet":
        path = "m/84'/1'/0'/0/0"  # Native SegWit (testnet)
        cryptocurrency = BitcoinTestnet
        print(f"Network: Testnet")
    elif network == "regtest":
        # Regtest에서는 legacy 주소 형식을 사용 (P2PKH)
        path = "m/44'/1'/0'/0/0"  # Legacy (regtest)
        cryptocurrency = BitcoinTestnet  # Regtest uses testnet settings
        print(f"Network: Regtest (Legacy)")
    else:
        print(f"Unknown network: {network}. Using regtest as default.")
        path = "m/44'/1'/0'/0/0"
        cryptocurrency = BitcoinTestnet
        network = "regtest"

    # HDWallet 객체 생성 (비트코인) - 올바른 네트워크 설정
    hdwallet: HDWallet = HDWallet(cryptocurrency=cryptocurrency)
    hdwallet.from_mnemonic(mnemonic=mnemonic_phrase)

    # 마스터 개인키 (확장 개인키)
    master_xprv = hdwallet.xprivate_key()
    print(f"Master XPRV: {master_xprv}")

    hdwallet.from_path(path=path)

    # 파생된 주소의 개인키 (WIF 형식)
    private_key_wif = hdwallet.wif()
    print(f"Private Key (WIF) for {path}: {private_key_wif}")
    
    # Regtest에서는 legacy 주소 형식 사용
    if network == "regtest":
        print(f"Corresponding Address: {hdwallet.p2pkh_address()}")
    else:
        print(f"Corresponding Address: {hdwallet.p2wpkh_address()}")
 
if __name__ == "__main__":
    # 명령행 인수에서 네트워크 환경을 받음
    network = sys.argv[1] if len(sys.argv) > 1 else "regtest"
    
    # 기존 니모닉이 있는지 확인 (두 번째 인수)
    existing_mnemonic = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_keys(network, existing_mnemonic)