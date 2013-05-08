#!/bin/bash

FILE=$1
CLOUD=$2

if [ "$CLOUD" == "ec2" ]; then
    set -- `ec2metadata | grep instance-type`
    TYPE=$2
elif [ "$CLOUD" == "gce" ]; then
    set -- `gcutil getinstance $HOSTNAME | grep 'machine'`
    set -- `echo $4 | tr "/" " "`
    TYPE=$2
else
    CLOUD="unknown"
    TYPE="unknown"
fi

DATE=`date +"%Y-%m-%d"`
TIME=`date +"%H:%M:%S"`
DIR=$HOME
RES_DIR=$DIR/perf-benchmarks/disk-io/results
LOG_DIR=$RES_DIR/$CLOUD/$DATE/$TYPE
LOG_NAME=$TIME-disk-io
LOG=$LOG_DIR/$LOG_NAME

/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh write-4k-1-2000-128M $FILE 128M write 4k 2000 1 /tmp/fio.conf

fio /tmp/fio.conf >> $LOG
