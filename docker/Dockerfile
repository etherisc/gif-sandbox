# this dockerfile from https://github.com/eth-brownie/brownie
FROM python:3.7

# Set up code directory
RUN mkdir -p /usr/src/app/brownie-setup
WORKDIR /usr/src/app

# Install linux dependencies
RUN apt-get update && apt-get install -y libssl-dev
RUN apt-get update && apt-get install -y npm

# Install Ganache chain
RUN npm install --global ganache-cli

# Install Brownie
RUN echo force-brownie-upgrade-0
RUN wget https://raw.githubusercontent.com/eth-brownie/brownie/master/requirements.txt

RUN pip install -r requirements.txt
RUN pip install eth-brownie

# Install FastAPI
RUN pip install fastapi
RUN pip install uvicorn

# force installation of solc in docker image
# solc version is defined in brownie-config.yaml
WORKDIR /usr/src/app/brownie-setup
RUN echo force-dependency-upgrade-0

RUN brownie init -f
COPY brownie-config.yaml /usr/src/app/brownie-setup
COPY Dummy.sol /usr/src/app/brownie-setup/contracts
RUN brownie compile --all

EXPOSE 8000

# Add some aliases
RUN echo "alias rm='rm -i'" >> /root/.bashrc
RUN echo "alias l='ls -CF'" >> /root/.bashrc
RUN echo "alias la='ls -A'" >> /root/.bashrc
RUN echo "alias ll='ls -alF'" >> /root/.bashrc

WORKDIR /projects

CMD [ "bash" ]