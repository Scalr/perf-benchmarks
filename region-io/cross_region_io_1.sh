#!/bin/bash

NETCAT_PORT=$1
DEST=/dev/null

echo 'run netcat on destination server'
sudo nc -l $NETCAT_PORT > $DEST

# FIXME with chef
sudo apt-get install -y iperf

echo 'run iperf server on destination server'
iperf -s -p 12345
