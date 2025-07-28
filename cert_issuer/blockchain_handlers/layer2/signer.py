import logging

import web3
from eth_utils import to_hex

from cert_issuer.errors import UnableToSignTxError
from cert_issuer.models import Signer


class Layer2Signer(Signer):
    def __init__(self, layer2_chain):
        self.layer2_chain = layer2_chain
        # Netcode ensures replay protection (see EIP155)
        if layer2_chain.external_display_value == 'polygonMainnet':
            self.netcode = 137
        elif layer2_chain.external_display_value == 'polygonMumbai':
            self.netcode = 80001
        elif layer2_chain.external_display_value == 'arbitrumOne':
            self.netcode = 42161
        elif layer2_chain.external_display_value == 'arbitrumGoerli':
            self.netcode = 421613
        elif layer2_chain.external_display_value == 'optimismMainnet':
            self.netcode = 10
        elif layer2_chain.external_display_value == 'optimismGoerli':
            self.netcode = 420
        else:
            self.netcode = None

    # wif = unencrypted private key as string in the first line of the supplied private key file
    def sign_message(self, wif, message_to_sign):
        pass

    def sign_transaction(self, wif, transaction_to_sign):
        ##try to sign the transaction.

        if isinstance(transaction_to_sign, dict):
            try:
                transaction_to_sign['chainId'] = self.netcode
                raw_tx = web3.Account.sign_transaction(transaction_to_sign, wif)["raw_transaction"]
                raw_tx_hex = to_hex(raw_tx)
                return raw_tx_hex
            except Exception as msg:
                logging.error('error occurred when Layer2 signing transaction: %s', msg)
                return {'error': True, 'message': msg}
        else:
            raise UnableToSignTxError('"sign_transaction()" expects a dict representing an unsigned transaction with fields such as "gas", "to", "data", etc. run "$ python cert_issuer -h" for more information on transaction configuration.') 