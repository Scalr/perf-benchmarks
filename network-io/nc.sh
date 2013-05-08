#!/bin/bash

NETCAT_PORT=$1

echo run netcat in listen mode on port $NETCAT_PORT
sudo killall -9 nc &>/dev/null
sudo nc -l $NETCAT_PORT 1>/dev/null
