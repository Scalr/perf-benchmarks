#!/bin/bash

NETCAT_PORT=$1

echo run netcat in listen mode on port $NETCAT_PORT
sudo nc -l $NETCAT_PORT > /dev/null
