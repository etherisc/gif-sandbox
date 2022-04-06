# this dockerfile from https://github.com/eth-brownie/brownie
FROM python:3.7

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install linux dependencies
RUN apt-get update && apt-get install -y libssl-dev
RUN apt-get update && apt-get install -y npm

# Install Ganache chain
RUN npm install --global ganache-cli

# Install Brownie
RUN wget https://raw.githubusercontent.com/eth-brownie/brownie/master/requirements.txt

RUN pip install -r requirements.txt
RUN pip install eth-brownie

# Install FastAPI
RUN pip install fastapi
RUN pip install uvicorn

EXPOSE 8000

# Add some aliases
RUN echo "alias rm='rm -i'" >> /root/.bashrc
RUN echo "alias l='ls -CF'" >> /root/.bashrc
RUN echo "alias la='ls -A'" >> /root/.bashrc
RUN echo "alias ll='ls -alF'" >> /root/.bashrc

WORKDIR /projects

CMD [ "bash" ]