#!/bin/bash

NAME=$1
FILE=$2
SIZE=$3
RW=$4
BS=$5
IOPS=$6
DEPTH=$7
OUT=$8
#OUT=$RW-$BS-$DEPTH-$IOPS-$SIZE

cat > $OUT << EOF
[global]
clocksource=cpu
randrepeat=0
ioengine=libaio
direct=1
size=128M

[$NAME]
ioscheduler=deadline
ramp_time=15
filename=$FILE
rate_iops=$IOPS
rw=$RW
size=$SIZE
bs=$BS
iodepth=$DEPTH
EOF


