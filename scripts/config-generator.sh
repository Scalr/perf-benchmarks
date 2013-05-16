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
runtime=180

[$NAME]
ioscheduler=deadline
ramp_time=30
filename=$FILE
rw=$RW
size=$SIZE
rate_iops=4000
bs=$BS
iodepth=$DEPTH
stonewall
EOF


