#!/bin/bash

# 니모닉을 사용하여 Bitcoin Core 지갑 생성 예시 스크립트

echo "🔧 니모닉을 사용하여 Bitcoin Core 지갑 생성하기"
echo "================================================"

# 1. 기존 니모닉 사용 (generate_mnemonic.py 활용)
echo "1️⃣ 기존 니모닉을 사용하여 개인키 생성..."
python generate_mnemonic.py regtest "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

echo ""
echo "2️⃣ 생성된 개인키를 Bitcoin Core에 가져오기..."
python import_mnemonic_to_bitcoin.py "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" regtest "my_mnemonic_wallet"

echo ""
echo "3️⃣ BIP39 니모닉 직접 가져오기 시도..."
python import_bip39_mnemonic.py "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" regtest "my_bip39_wallet"

echo ""
echo "4️⃣ 수동으로 지갑 생성 및 개인키 추출..."
python import_bip39_mnemonic.py "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" regtest "my_manual_wallet"

echo ""
echo "5️⃣ Bitcoin Core 명령어로 직접 확인..."
echo "지갑 목록:"
bitcoin-cli -regtest listwallets

echo ""
echo "현재 로드된 지갑 정보:"
bitcoin-cli -regtest getwalletinfo

echo ""
echo "6️⃣ cert-issuer 설정을 위한 정보..."
echo "conf.ini 파일에 다음을 추가하세요:"
echo "issuing_address = <생성된_주소>"
echo "key_file = <개인키_파일_경로>"
echo "chain = bitcoin_regtest"

echo ""
echo "7️⃣ regtest 모드에서 코인 생성 및 전송..."
echo "bitcoin-cli -regtest generate 101"
echo "bitcoin-cli -regtest sendtoaddress <생성된_주소> 5"

echo ""
echo "✅ 완료! 이제 cert-issuer를 사용하여 인증서를 발행할 수 있습니다." 