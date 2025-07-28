import logging
import os

from cert_core import UnknownChainError

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler, CertificateBatchWebHandler, CertificateWebV3Handler
from cert_issuer.blockchain_handlers.layer2.connectors import Layer2ServiceProviderConnector
from cert_issuer.blockchain_handlers.layer2.signer import Layer2Signer
from cert_issuer.blockchain_handlers.layer2.transaction_handlers import Layer2TransactionHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager

ONE_BILLION = 1000000000


class Layer2TransactionCostConstants(object):
    def __init__(self, max_priority_fee_per_gas, recommended_gas_price, recommended_gas_limit):
        self.max_priority_fee_per_gas = max_priority_fee_per_gas
        self.recommended_gas_price = recommended_gas_price
        self.recommended_gas_limit = recommended_gas_limit
        logging.info('Set cost constants to recommended_gas_price=%f Gwei, recommended_gas_limit=%d gas',
            self.recommended_gas_price / ONE_BILLION, self.recommended_gas_limit)
        if self.max_priority_fee_per_gas:
            logging.info('and max_priority_fee_per_gas=%f Gwei', self.max_priority_fee_per_gas / ONE_BILLION)

    def get_recommended_max_cost(self):
        return self.recommended_gas_price * self.recommended_gas_limit

    def get_max_priority_fee_per_gas(self):
        return self.max_priority_fee_per_gas

    def get_gas_price(self):
        return self.recommended_gas_price

    def get_gas_limit(self):
        return self.recommended_gas_limit


def initialize_signer(app_config):
    if app_config.safe_mode:
        return FileSecretManager(app_config.issuing_address, app_config.chain)
    else:
        return FileSecretManager(app_config.issuing_address, app_config.chain)


def instantiate_blockchain_handlers(app_config, file_mode=True):
    issuing_address = app_config.issuing_address
    chain = app_config.chain
    secret_manager = initialize_signer(app_config)

    certificate_batch_handler = (CertificateBatchHandler if file_mode else CertificateBatchWebHandler)(
        secret_manager=secret_manager,
        certificate_handler=(CertificateV3Handler if file_mode else CertificateWebV3Handler)(app_config),
        merkle_tree=MerkleTreeGenerator(),
        config=app_config
    )

    if chain.is_mock_type():
        transaction_handler = MockTransactionHandler()
    # layer2 chains
    elif chain.is_layer2_type():
        nonce = app_config.nonce
        connector = Layer2ServiceProviderConnector(chain, app_config)

        if app_config.gas_price_dynamic:
            gas_price = connector.gas_price()
        else:
            gas_price = app_config.gas_price

        cost_constants = Layer2TransactionCostConstants(app_config.max_priority_fee_per_gas,
                                                       gas_price, app_config.gas_limit)

        transaction_handler = Layer2TransactionHandler(connector, nonce, cost_constants, secret_manager,
                                                      issuing_address=issuing_address)

    return certificate_batch_handler, transaction_handler, connector 