#!/bin/bash

FILE=$1
SIZE=$2
CLOUD=$3

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

IOPS=2000


echo WRITE
RW="write"

BS=4k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



BS=4k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



echo RANDWRITE
RW="randwrite"

BS=4k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



BS=4k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



echo READ
RW="read" 

BS=4k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG




BS=4k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG



echo RANDREAD
RW="randread" 

BS=4k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=1
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG




BS=4k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=128k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

BS=256k
DEPTH=8
echo -e "\n#" >> $LOG
echo ======SIZE-$SIZE===RW-$RW===BS-$BS===IOPS-$IOPS===DEPTH-$DEPTH====== >> $LOG
echo -e "\n#" >> $LOG
/bin/bash $DIR/perf-benchmarks/disk-io/fio/config_generator.sh name $FILE $SIZE $RW $BS $IOPS $DEPTH /tmp/fio.conf
fio --timeout=300 /tmp/fio.conf >> $LOG

cd $RES_DIR 

echo "committing  results ..."
git fetch origin
git pull origin master
git add $LOG
git commit -m "$CLOUD $TYPE $LOG_NAME"
git push -u origin master
