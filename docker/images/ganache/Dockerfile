FROM phusion/baseimage:focal-1.0.0

WORKDIR /app 

RUN rm /bin/sh && ln -s /bin/bash /bin/sh && \
    sed -i 's/^mesg n$/tty -s \&\& mesg n/g' /root/.profile

# install additional packages
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    iputils-ping \
    tree \
    nano

# install node 16 (and npm)
RUN /bin/bash -l -c "curl -sSL https://deb.nodesource.com/setup_16.x | bash -"
RUN /bin/bash -l -c "apt-get install nodejs -y"

# install web3 and ethers api to interact with blockchain
# this allows interactive usage of the container without any additional installs
RUN /bin/bash -l -c "npm install -g web3"
RUN /bin/bash -l -c "npm install -g --save ethers"

# install ganache (local chain for testing)
RUN /bin/bash -l -c "npm install -g ganache-cli"

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ganache setup
# port: 8545 (ganache default port)
# mnemonic: "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
# private key: 0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3
# db path: /var/lib/ganache/data
CMD ["ganache-cli", "--port", "8545", "--mnemonic", "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat", "--accounts", "10",  "--defaultBalanceEther", "10000", "--networkId", "1234", "--chainId", "1234", "--db", "/var/lib/ganache/data", "-h", "0.0.0.0"]