#!/bin/bash

NETCAT_PORT=$1

echo run netcat in listen mode on port $NETCAT_PORT
sudo killall -9 nc &>/dev/null
sudo nc -l $NETCAT_PORT 1>/dev/null

echo run iperf server
sudo killall -9 iperf &>/dev/null
sudo iperf -s -p 1234 &>/dev/null
