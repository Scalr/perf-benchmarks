#!/bin/bash

NAME=$1
SIZE=$2
RW=$3
BS=$4
FILE=$5
OUT=$6

cat > $OUT << EOF
[global]
clocksource=cpu
randrepeat=0
ioengine=libaio
direct=1
size=128M

[$NAME]
time_based
ioscheduler=deadline
ramp_time=15
filename=$FILE
rw=$RW
size=$SIZE
bs=$BS
iodepth=$DEPTH
stonewall
EOF


