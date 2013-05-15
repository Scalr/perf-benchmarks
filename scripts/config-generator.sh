#!/bin/bash

NAME=$1
FILE=$2
SIZE=$3
RW=$4
BS=$5
DEPTH=$6
OUT=$7

cat > $OUT << EOF
[global]
clocksource=cpu
randrepeat=0
ioengine=libaio
direct=1
runtime=600

[$NAME]
ioscheduler=deadline
ramp_time=15
filename=$FILE
rw=$RW
size=$SIZE
bs=$BS
iodepth=$DEPTH
stonewall
EOF


