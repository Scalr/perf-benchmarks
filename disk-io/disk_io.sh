#!/bin/bash

FILE=$1
CLOUD=$2

DIR=$HOME
RES_DIR=$DIR/perf-benchmarks/disk-io/results

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
LOG_DIR=$RES_DIR/$CLOUD/$DATE/$TYPE
LOG_NAME=$TIME-disk-io
LOG=$LOG_DIR/$LOG_NAME

if [ ! -d $LOG_DIR ]; then
    mkdir -p $LOG_DIR
fi

SIZE=64M
IOPS=2000



RW="write"

BS=4k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



BS=4k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



RW="randwrite"

BS=4k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



BS=4k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



RW="read" 

BS=4k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG




BS=4k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



RW="randread" 

BS=4k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG




BS=4k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo "#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo "#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG
