FROM lncm/bitcoind:v27.2
MAINTAINER Kim Duffy "kimhd@mit.edu"

USER root

COPY . /cert-issuer
COPY conf_regtest.ini /etc/cert-issuer/conf.ini

RUN apk add --update \
        bash \
        ca-certificates \
        curl \
        gcc \
        gmp-dev \
        libffi-dev \
        libressl-dev \
        libxml2-dev \
        libxslt-dev \
        linux-headers \
        make \
        musl-dev \
        python3 \
        python3-dev \
        tar \
        git \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && pip3 install Cython \
    && pip3 install wheel \
    && mkdir -p /etc/cert-issuer/data/unsigned_certificates \
    && mkdir /etc/cert-issuer/data/blockchain_certificates \
    && mkdir ~/.bitcoin \
    && echo $'[regtest]\nrpcuser=foo\nrpcpassword=bar\nrpcport=8332\nregtest=1\nrelaypriority=0\nrpcallowip=127.0.0.1\nrpcconnect=127.0.0.1\n' > /root/.bitcoin/bitcoin.conf \
    && pip3 install /cert-issuer/. \
    && pip3 install -r /cert-issuer/ethereum_requirements.txt \
    && rm -r /usr/lib/python*/ensurepip \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache

# ENTRYPOINT bitcoind -daemon && bash
# Activate virtual environment and start services

ENTRYPOINT ["/bin/bash", "-c", "bitcoind -regtest -daemon && sleep 10 && source .venv/bin/activate && exec bash"]
