#!/bin/bash

GIF_CONTRACTS_PKG_DIR=`find . ~/ -name brownie-config.yaml | grep gif-contracts | xargs dirname`
touch $GIF_CONTRACTS_PKG_DIR/.env
