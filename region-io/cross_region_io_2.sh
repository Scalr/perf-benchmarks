#!/bin/bash

SSH_KEY=$1
USER=$2
DEST_IP=$3
NETCAT_PORT=$4
FILE_SIZE=$5
CLOUD=$6
SOURCE=/tmp/io_benchmarks
DEST=/dev/null
LOG=results/region-io-`date +"%Y-%m-%d-%H:%M:%S"`

if [ ! -d results ]; then
    mkdir results
fi

truncate -s $FILE_SIZE $SOURCE

echo "# cross-region io benchmark" >> $LOG
echo `date +%s` >> $LOG
echo `date` >> $LOG

if [ "$CLOUD" == "ec2" ]; then
    echo `ec2metadata | grep 'availability-zone'` >> $LOG
    echo `ec2metadata | grep 'machine'` >> $LOG
fi

if [ "$CLOUD" == "gce" ]; then
    echo `gcutil getinstance $HOSTNAME | grep 'zone'` >> $LOG
    echo `gcutil getinstance $HOSTNAME | grep 'zone'` >> $LOG
fi

echo -e "File size" $FILE_SIZE "\n" >> $LOG

echo "nc" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU\n" cat $SOURCE | nc $DEST_IP $NETCAT_PORT -q 0; } 2>>$LOG

echo "scp" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU\n" scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

# FIXME with chef
sudo apt-get install -y iperf

echo "iperf" >> $LOG
iperf -c $DEST_IP -p 12345 -t 60 | grep '/sec' >> $LOG


ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 nc'
ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 iperf'
