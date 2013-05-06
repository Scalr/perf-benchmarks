#!/bin/bash

USER=$1
DEST_IP=$2
FILE_SIZE=$3
SSH_KEY=$HOME/.ssh/id_rsa
SOURCE=/tmp/io_benchmarks
DEST=/tmp/io_benchmarks
NETCAT_PORT=666
LOG=log/region-io

if [ -f log ]; then
    mkdir log
fi

truncate -s $FILE_SIZE $SOURCE

echo `/bin/date` >> $LOG

echo -e "File size" $FILE_SIZE "\n" >> $LOG

echo "NetCut" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /bin/cat $SOURCE | /bin/nc $DEST_IP $NETCAT_PORT ; } 2>>$LOG

echo "Single thread scp" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /usr/bin/scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

echo -e "\n" >> $LOG

