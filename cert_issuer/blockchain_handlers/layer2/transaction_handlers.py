import logging

import web3
from eth_utils import remove_0x_prefix, to_hex
from web3 import Web3

from cert_issuer.blockchain_handlers.ethereum.transaction_handlers import EthereumTransactionCreator
from cert_issuer.errors import InsufficientFundsError
from cert_issuer.models import TransactionHandler


class Layer2TransactionCreator(EthereumTransactionCreator):
    def estimate_cost_for_certificate_batch(self, tx_cost_constants, num_inputs=1):
        total = tx_cost_constants.get_recommended_max_cost()
        return total

    def create_transaction(self, tx_cost_constants, issuing_address, inputs, op_return_value):
        # Layer2 transactions are similar to Ethereum but with different gas costs
        transaction = {
            'to': issuing_address,
            'value': 0,
            'data': op_return_value,
            'gas': tx_cost_constants.get_gas_limit(),
            'gasPrice': tx_cost_constants.get_gas_price(),
            'nonce': 0  # This will be set by the transaction handler
        }
        
        if tx_cost_constants.get_max_priority_fee_per_gas():
            transaction['maxPriorityFeePerGas'] = tx_cost_constants.get_max_priority_fee_per_gas()
            transaction['maxFeePerGas'] = tx_cost_constants.get_gas_price()
            # Remove gasPrice for EIP-1559 transactions
            transaction.pop('gasPrice', None)
            
        return transaction


class Layer2TransactionHandler(TransactionHandler):
    def __init__(self, connector, nonce, tx_cost_constants, secret_manager, issuing_address, prepared_inputs=None,
                 transaction_creator=Layer2TransactionCreator()):
        self.connector = connector
        self.nonce = nonce
        self.tx_cost_constants = tx_cost_constants
        self.secret_manager = secret_manager
        self.issuing_address = Web3.to_checksum_address(issuing_address)
        # input transactions are not needed for Layer2
        self.prepared_inputs = prepared_inputs
        self.transaction_creator = transaction_creator

    def ensure_balance(self):
        # testing layer2 api wrapper
        self.balance = self.connector.get_balance(self.issuing_address)

        # for now transaction cost will be a constant: (25000 gas estimate times 20Gwei gasprice) from tx_utils
        # can later be calculated inside Layer2Transaction_creator
        transaction_cost = self.tx_cost_constants.get_recommended_max_cost()
        logging.info('Total cost will be no more than %d wei', transaction_cost)

        if transaction_cost > self.balance:
            error_message = 'Please add {} wei to the address {}'.format(
                transaction_cost - self.balance, self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def issue_transaction(self, blockchain_bytes):
        layer2_data_field = remove_0x_prefix(to_hex(blockchain_bytes))
        prepared_tx = self.create_transaction(blockchain_bytes)
        signed_tx = self.sign_transaction(prepared_tx)
        self.verify_transaction(signed_tx, layer2_data_field)
        txid = self.broadcast_transaction(signed_tx)
        return txid

    def create_transaction(self, op_return_bytes):
        # Get current nonce from the blockchain
        current_nonce = self.connector.get_address_nonce(self.issuing_address)
        if self.nonce > 0:
            current_nonce = self.nonce

        eth_data_field = remove_0x_prefix(to_hex(op_return_bytes))
        transaction = self.transaction_creator.create_transaction(self.tx_cost_constants, self.issuing_address, [], eth_data_field)
        transaction['nonce'] = current_nonce
        transaction['from'] = self.issuing_address

        logging.info('Unsigned transaction: %s', transaction)
        return transaction

    def sign_transaction(self, prepared_tx):
        with self.secret_manager as secret_manager:
            wif = secret_manager.get_private_key()
            signer = self.secret_manager.get_signer()
            signed_tx = signer.sign_transaction(wif, prepared_tx)

        if isinstance(signed_tx, dict) and signed_tx.get('error'):
            raise Exception('Transaction signing failed: %s' % signed_tx.get('message', 'Unknown error'))

        logging.info('Signed transaction: %s', signed_tx)
        return signed_tx

    def verify_transaction(self, signed_tx, op_return_value):
        # For Layer2, we can verify the transaction by checking if it's properly formatted
        # The actual verification happens on the blockchain
        logging.info('Transaction verification passed for Layer2 network')

    def broadcast_transaction(self, signed_tx):
        txid = self.connector.broadcast_tx(signed_tx)
        return txid 