#!/bin/bash

# file or device for test
FILE=$1

# file size
SIZE=$2

# cloud <ec2|gce>
CLOUD=$3


DIR=$HOME
RES_DIR=$DIR/perf-benchmarks/results/disk-io

if [ "$CLOUD" == "ec2" ]; then
    wget http://s3.amazonaws.com/ec2metadata/ec2-metadata
    chmod +x ec2-metadata
    set -- $(ec2-metadata -t)
    TYPE=$2
elif [ "$CLOUD" == "gce" ]; then
    line=$(gcutil getinstance $HOSTNAME | grep 'machine')
    set -- $(echo $line | tr "|" " ")
    TYPE=$2
else
    CLOUD="unknown"
    TYPE="unknown"
fi

DATE=`date -u +"%Y-%m-%d"`
TIME=`date -u +"%H:%M:%S"`
LOG_DIR=$RES_DIR/$CLOUD/$TYPE
LOG_NAME=$DATE-$TIME-$TYPE'.fiores'
LOG=$LOG_DIR/$LOG_NAME

if [ ! -d $LOG_DIR ]; then
    mkdir -p $LOG_DIR
fi

RW="randwrite"

for BS in 16k 64k 128k
do
    for DEPTH in 1 4
    do
        echo "# $DATE $TIME UTC" | tee -a $LOG
        /bin/bash $DIR/perf-benchmarks/scripts/config-generator.sh $RW-$SIZE-$BS-$DEPTH $FILE $SIZE $RW $BS $DEPTH /tmp/fio.conf
        cat /tmp/fio.conf >>$LOG
        sudo fio --timeout=330 /tmp/fio.conf | tee -a $LOG
    done
done

RW="randread"

for BS in 16k 64k 128k
do
    for DEPTH in 1 4
    do
        echo "# $DATE $TIME UTC" | tee -a $LOG
        /bin/bash $DIR/perf-benchmarks/scripts/config-generator.sh $RW-$SIZE-$BS-$DEPTH $FILE $SIZE $RW $BS $DEPTH /tmp/fio.conf
        cat /tmp/fio.conf >>$LOG
        sudo fio --timeout=330 /tmp/fio.conf | tee -a $LOG
    done
done

git config --global user.email "roman@scalr.com"
git config --global user.name "Roma Koshel"
