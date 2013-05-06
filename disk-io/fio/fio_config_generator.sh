#!/bin/bash

NAME=$1
SIZE=$2
RW=$3
BS=$4
DIR=$5
OUT=$6

cat > $OUT << EOF
[$NAME]
ramp_time=15
rw=$RW
size=$SIZE
bs=$BS
directory=$DIR
EOF


