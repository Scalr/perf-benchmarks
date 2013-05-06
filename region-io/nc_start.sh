#!/bin/bash

NETCAT_PORT=$1
DEST=$2

echo 'run netcat on destination server'
sudo nc -l $NETCAT_PORT > $DEST
