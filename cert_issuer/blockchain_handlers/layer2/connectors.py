import logging
import time

import requests
import web3
from web3 import Web3, HTTPProvider

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

from cert_core import Chain
from cert_issuer.models import ServiceProviderConnector
from cert_issuer.errors import BroadcastError

BROADCAST_RETRY_INTERVAL = 30
MAX_BROADCAST_ATTEMPTS = 3


class Layer2ServiceProviderConnector(ServiceProviderConnector):
    def __init__(
            self,
            layer2_chain,
            app_config,
            local_node=False):
        self.layer2_chain = layer2_chain
        self.local_node = local_node
        self.connectors = {}

        # Configure Polygon connectors
        polygon_provider_list = []
        if hasattr(app_config, 'polygon_rpc_url'):
            self.polygon_rpc_url = app_config.polygon_rpc_url
            polygon_provider_list.append(Layer2RPCProvider(self.polygon_rpc_url))
        polygon_provider_list.append(PolygonscanBroadcaster('https://api.polygonscan.com/api', app_config.polygonscan_api_token))
        self.connectors[Chain.polygon_mainnet] = polygon_provider_list

        # Configure Polygon Mumbai testnet connectors
        mumbai_provider_list = []
        if hasattr(app_config, 'mumbai_rpc_url'):
            self.mumbai_rpc_url = app_config.mumbai_rpc_url
            mumbai_provider_list.append(Layer2RPCProvider(self.mumbai_rpc_url))
        mumbai_provider_list.append(PolygonscanBroadcaster('https://api-testnet.polygonscan.com/api', app_config.polygonscan_api_token))
        self.connectors[Chain.polygon_mumbai] = mumbai_provider_list

        # Configure Arbitrum One connectors
        arbitrum_provider_list = []
        if hasattr(app_config, 'arbitrum_rpc_url'):
            self.arbitrum_rpc_url = app_config.arbitrum_rpc_url
            arbitrum_provider_list.append(Layer2RPCProvider(self.arbitrum_rpc_url))
        arbitrum_provider_list.append(ArbiscanBroadcaster('https://api.arbiscan.io/api', app_config.arbiscan_api_token))
        self.connectors[Chain.arbitrum_one] = arbitrum_provider_list

        # Configure Arbitrum Goerli testnet connectors
        arbitrum_goerli_provider_list = []
        if hasattr(app_config, 'arbitrum_goerli_rpc_url'):
            self.arbitrum_goerli_rpc_url = app_config.arbitrum_goerli_rpc_url
            arbitrum_goerli_provider_list.append(Layer2RPCProvider(self.arbitrum_goerli_rpc_url))
        arbitrum_goerli_provider_list.append(ArbiscanBroadcaster('https://api-goerli.arbiscan.io/api', app_config.arbiscan_api_token))
        self.connectors[Chain.arbitrum_goerli] = arbitrum_goerli_provider_list

        # Configure Optimism connectors
        optimism_provider_list = []
        if hasattr(app_config, 'optimism_rpc_url'):
            self.optimism_rpc_url = app_config.optimism_rpc_url
            optimism_provider_list.append(Layer2RPCProvider(self.optimism_rpc_url))
        optimism_provider_list.append(OptimisticEtherscanBroadcaster('https://api-optimistic.etherscan.io/api', app_config.optimistic_etherscan_api_token))
        self.connectors[Chain.optimism_mainnet] = optimism_provider_list

        # Configure Optimism Goerli testnet connectors
        optimism_goerli_provider_list = []
        if hasattr(app_config, 'optimism_goerli_rpc_url'):
            self.optimism_goerli_rpc_url = app_config.optimism_goerli_rpc_url
            optimism_goerli_provider_list.append(Layer2RPCProvider(self.optimism_goerli_rpc_url))
        optimism_goerli_provider_list.append(OptimisticEtherscanBroadcaster('https://api-goerli-optimistic.etherscan.io/api', app_config.optimistic_etherscan_api_token))
        self.connectors[Chain.optimism_goerli] = optimism_goerli_provider_list

    def get_providers_for_chain(self, chain, local_node=False):
        return self.connectors[chain]

    def get_balance(self, address):
        for m in self.get_providers_for_chain(self.layer2_chain, self.local_node):
            try:
                logging.debug('m=%s', m)
                balance = m.get_balance(address)
                return balance
            except Exception as e:
                logging.warning(e)
                pass
        return 0

    def gas_price(self):
        for m in self.get_providers_for_chain(self.layer2_chain, self.local_node):
            try:
                logging.info('m=%s', m)
                gas_price = m.gas_price()
                return gas_price
            except Exception as e:
                logging.info(e)
                pass
        return 0

    def get_address_nonce(self, address):
        for m in self.get_providers_for_chain(self.layer2_chain, self.local_node):
            try:
                nonce = m.get_address_nonce(address)
                return nonce
            except Exception as e:
                logging.warning(e)
                pass
        return 0

    def broadcast_tx(self, tx):
        for attempt in range(MAX_BROADCAST_ATTEMPTS):
            for m in self.get_providers_for_chain(self.layer2_chain, self.local_node):
                try:
                    txid = m.broadcast_tx(tx)
                    logging.info('Broadcast transaction with txid %s', txid)
                    return txid
                except Exception as e:
                    logging.warning('Broadcast attempt %d failed: %s', attempt + 1, e)
                    pass
            if attempt < MAX_BROADCAST_ATTEMPTS - 1:
                logging.info('Retrying broadcast in %d seconds...', BROADCAST_RETRY_INTERVAL)
                time.sleep(BROADCAST_RETRY_INTERVAL)
        raise BroadcastError('Failed to broadcast transaction after %d attempts' % MAX_BROADCAST_ATTEMPTS)


class Layer2RPCProvider(object):
    def __init__(self, layer2_url):
        self.web3 = Web3(HTTPProvider(layer2_url))

    def broadcast_tx(self, tx):
        tx_hash = self.web3.eth.send_raw_transaction(tx)
        return self.web3.to_hex(tx_hash)

    def get_balance(self, address):
        balance = self.web3.eth.get_balance(address)
        return balance

    def get_address_nonce(self, address):
        nonce = self.web3.eth.get_transaction_count(address)
        return nonce

    def gas_price(self):
        gas_price = self.web3.eth.gas_price
        return gas_price


class PolygonscanBroadcaster(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def send_request(self, method, url, data=None):
        if method == 'GET':
            response = requests.get(url, params=data)
        else:
            response = requests.post(url, data=data)
        return response.json()

    def broadcast_tx(self, tx):
        data = {
            'module': 'proxy',
            'action': 'eth_sendRawTransaction',
            'hex': tx,
            'apikey': self.api_token
        }
        response = self.send_request('POST', self.base_url, data)
        if response.get('status') == '1':
            return response.get('result')
        else:
            raise BroadcastError('Polygonscan broadcast failed: %s' % response.get('message', 'Unknown error'))

    def get_balance(self, address):
        data = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0'))
        else:
            raise Exception('Failed to get balance: %s' % response.get('message', 'Unknown error'))

    def gas_price(self):
        data = {
            'module': 'gastracker',
            'action': 'gasoracle',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            result = response.get('result', {})
            return int(result.get('SafeGasPrice', '20000000000')) * 10**9  # Convert to wei
        else:
            return 20000000000  # Default gas price

    def get_address_nonce(self, address):
        data = {
            'module': 'proxy',
            'action': 'eth_getTransactionCount',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0x0'), 16)
        else:
            raise Exception('Failed to get nonce: %s' % response.get('message', 'Unknown error'))


class ArbiscanBroadcaster(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def send_request(self, method, url, data=None):
        if method == 'GET':
            response = requests.get(url, params=data)
        else:
            response = requests.post(url, data=data)
        return response.json()

    def broadcast_tx(self, tx):
        data = {
            'module': 'proxy',
            'action': 'eth_sendRawTransaction',
            'hex': tx,
            'apikey': self.api_token
        }
        response = self.send_request('POST', self.base_url, data)
        if response.get('status') == '1':
            return response.get('result')
        else:
            raise BroadcastError('Arbiscan broadcast failed: %s' % response.get('message', 'Unknown error'))

    def get_balance(self, address):
        data = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0'))
        else:
            raise Exception('Failed to get balance: %s' % response.get('message', 'Unknown error'))

    def gas_price(self):
        data = {
            'module': 'gastracker',
            'action': 'gasoracle',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            result = response.get('result', {})
            return int(result.get('SafeGasPrice', '20000000000')) * 10**9  # Convert to wei
        else:
            return 20000000000  # Default gas price

    def get_address_nonce(self, address):
        data = {
            'module': 'proxy',
            'action': 'eth_getTransactionCount',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0x0'), 16)
        else:
            raise Exception('Failed to get nonce: %s' % response.get('message', 'Unknown error'))


class OptimisticEtherscanBroadcaster(object):
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def send_request(self, method, url, data=None):
        if method == 'GET':
            response = requests.get(url, params=data)
        else:
            response = requests.post(url, data=data)
        return response.json()

    def broadcast_tx(self, tx):
        data = {
            'module': 'proxy',
            'action': 'eth_sendRawTransaction',
            'hex': tx,
            'apikey': self.api_token
        }
        response = self.send_request('POST', self.base_url, data)
        if response.get('status') == '1':
            return response.get('result')
        else:
            raise BroadcastError('Optimistic Etherscan broadcast failed: %s' % response.get('message', 'Unknown error'))

    def get_balance(self, address):
        data = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0'))
        else:
            raise Exception('Failed to get balance: %s' % response.get('message', 'Unknown error'))

    def gas_price(self):
        data = {
            'module': 'gastracker',
            'action': 'gasoracle',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            result = response.get('result', {})
            return int(result.get('SafeGasPrice', '20000000000')) * 10**9  # Convert to wei
        else:
            return 20000000000  # Default gas price

    def get_address_nonce(self, address):
        data = {
            'module': 'proxy',
            'action': 'eth_getTransactionCount',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_token
        }
        response = self.send_request('GET', self.base_url, data)
        if response.get('status') == '1':
            return int(response.get('result', '0x0'), 16)
        else:
            raise Exception('Failed to get nonce: %s' % response.get('message', 'Unknown error')) 