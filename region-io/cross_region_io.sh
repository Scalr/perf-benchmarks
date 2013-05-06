#!/bin/bash

USER=$1
DEST_IP=$2
FILE_SIZE=$3
NETCAT_PORT=$4
SSH_KEY=$HOME/.ssh/id_rsa
SOURCE=/tmp/io_benchmarks
DEST=$5
LOG=log/region-io

if [ ! -d log ]; then
    mkdir log
fi

truncate -s $FILE_SIZE $SOURCE

echo `/bin/date` >> $LOG
echo `/usr/bin/ec2metadata  | grep 'availability-zone'` >> $LOG
echo `/usr/bin/ec2metadata  | grep 'instance-type'` >> $LOG

echo -e "File size" $FILE_SIZE "\n" >> $LOG

echo "NetCut" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /bin/cat $SOURCE | /bin/nc $DEST_IP $NETCAT_PORT ; } 2>>$LOG

echo "Single thread scp" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /usr/bin/scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

