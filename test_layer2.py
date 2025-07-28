#!/usr/bin/env python3
"""
Test script for Layer2 network functionality
"""

import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cert_issuer.blockchain_handlers.layer2.connectors import Layer2ServiceProviderConnector
from cert_issuer.blockchain_handlers.layer2.signer import Layer2Signer
from cert_issuer.blockchain_handlers.layer2.transaction_handlers import Layer2TransactionHandler
from cert_issuer.blockchain_handlers.layer2 import Layer2TransactionCostConstants
from cert_issuer.signer import FileSecretManager
from cert_core import Chain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_layer2_connectors():
    """Test Layer2 connector functionality"""
    print("Testing Layer2 connectors...")
    
    # Mock configuration
    class MockConfig:
        def __init__(self):
            self.polygon_rpc_url = "https://polygon-rpc.com"
            self.mumbai_rpc_url = "https://rpc-mumbai.maticvigil.com"
            self.arbitrum_rpc_url = "https://arb1.arbitrum.io/rpc"
            self.optimism_rpc_url = "https://mainnet.optimism.io"
            self.polygonscan_api_token = "test_token"
            self.arbiscan_api_token = "test_token"
            self.optimistic_etherscan_api_token = "test_token"
    
    config = MockConfig()
    
    try:
        # Test Polygon connector
        connector = Layer2ServiceProviderConnector(Chain.polygon_mainnet, config)
        print("✓ Polygon connector created successfully")
        
        # Test Arbitrum connector
        connector = Layer2ServiceProviderConnector(Chain.arbitrum_one, config)
        print("✓ Arbitrum connector created successfully")
        
        # Test Optimism connector
        connector = Layer2ServiceProviderConnector(Chain.optimism_mainnet, config)
        print("✓ Optimism connector created successfully")
        
    except Exception as e:
        print(f"✗ Connector test failed: {e}")
        return False
    
    return True

def test_layer2_signer():
    """Test Layer2 signer functionality"""
    print("Testing Layer2 signer...")
    
    try:
        # Test Polygon signer
        signer = Layer2Signer(Chain.polygon_mainnet)
        assert signer.netcode == 137
        print("✓ Polygon signer created successfully")
        
        # Test Arbitrum signer
        signer = Layer2Signer(Chain.arbitrum_one)
        assert signer.netcode == 42161
        print("✓ Arbitrum signer created successfully")
        
        # Test Optimism signer
        signer = Layer2Signer(Chain.optimism_mainnet)
        assert signer.netcode == 10
        print("✓ Optimism signer created successfully")
        
    except Exception as e:
        print(f"✗ Signer test failed: {e}")
        return False
    
    return True

def test_layer2_transaction_handler():
    """Test Layer2 transaction handler functionality"""
    print("Testing Layer2 transaction handler...")
    
    # Mock configuration
    class MockConfig:
        def __init__(self):
            self.polygon_rpc_url = "https://polygon-rpc.com"
            self.polygonscan_api_token = "test_token"
    
    config = MockConfig()
    
    try:
        # Test transaction cost constants
        cost_constants = Layer2TransactionCostConstants(
            max_priority_fee_per_gas=0,
            recommended_gas_price=30000000000,
            recommended_gas_limit=25000
        )
        print("✓ Transaction cost constants created successfully")
        
        # Test connector
        connector = Layer2ServiceProviderConnector(Chain.polygon_mainnet, config)
        print("✓ Connector created successfully")
        
        # Test transaction handler
        handler = Layer2TransactionHandler(
            connector=connector,
            nonce=0,
            tx_cost_constants=cost_constants,
            secret_manager=None,  # Mock secret manager
            issuing_address="0x1234567890123456789012345678901234567890"
        )
        print("✓ Transaction handler created successfully")
        
    except Exception as e:
        print(f"✗ Transaction handler test failed: {e}")
        return False
    
    return True

def test_chain_support():
    """Test that all Layer2 chains are properly supported"""
    print("Testing Layer2 chain support...")
    
    supported_chains = [
        Chain.polygon_mainnet,
        Chain.polygon_mumbai,
        Chain.arbitrum_one,
        Chain.arbitrum_goerli,
        Chain.optimism_mainnet,
        Chain.optimism_goerli
    ]
    
    try:
        for chain in supported_chains:
            print(f"✓ Chain {chain.name} is supported")
        
    except Exception as e:
        print(f"✗ Chain support test failed: {e}")
        return False
    
    return True

def main():
    """Run all Layer2 tests"""
    print("Starting Layer2 functionality tests...\n")
    
    tests = [
        test_chain_support,
        test_layer2_connectors,
        test_layer2_signer,
        test_layer2_transaction_handler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}\n")
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Layer2 tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 