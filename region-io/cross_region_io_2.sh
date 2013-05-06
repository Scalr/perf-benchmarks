#!/bin/bash

SSH_KEY=$1
USER=$2
DEST_IP=$3
FILE_SIZE=$4
NETCAT_PORT=$5
CLOUD=$6
SOURCE=/tmp/io_benchmarks
DEST=/dev/null
LOG=results/region-io-`date +"%Y-%m-%d-%H:%M:%S"`

if [ ! -d results ]; then
    mkdir results
fi

truncate -s $FILE_SIZE $SOURCE

echo "# cross-region io benchmark" >> $LOG
echo `/bin/date` >> $LOG

if [ "$CLOUD" == "ec2" ]; then
    echo `/usr/bin/ec2metadata | grep 'availability-zone'` >> $LOG
    echo `/usr/bin/ec2metadata | grep 'machine'` >> $LOG
fi

if [ "$CLOUD" == "gce" ]; then
    echo `/usr/bin/gcutil getinstance $HOSTNAME | grep 'zone'` >> $LOG
    echo `/usr/bin/gcutil getinstance $HOSTNAME | grep 'zone'` >> $LOG
fi

echo -e "File size" $FILE_SIZE "\n" >> $LOG

echo "nc" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /bin/cat $SOURCE | /bin/nc $DEST_IP $NETCAT_PORT ; } 2>>$LOG

echo "scp" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percenage of the CPU\n" /usr/bin/scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

# FIXME with chef
sudo apt-get install -y iperf

echo "iperf" >> $LOG
/usr/bin/iperf -c $DEST_IP -p 12345 -t 60 | grep 'Gbits/sec' >> $LOG
