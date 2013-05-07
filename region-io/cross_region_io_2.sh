#!/bin/bash

SSH_KEY=$1
USER=$2
DEST_IP=$3
NETCAT_PORT=$4
FILE_SIZE=$5
CLOUD=$6
SOURCE=/tmp/io_benchmarks
DEST=/dev/null
LOG_DIR=$HOME/perf-benchmarks/region-io/results

if [ ! -d $LOG_DIR ]; then
    mkdir $LOG_DIR
fi

truncate -s $FILE_SIZE $SOURCE

if [ "$CLOUD" == "ec2" ]; then
    set -- `ec2metadata | grep availability-zone`
    FROM=$2
    set -- `ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'ec2metadata | grep availability-zone'`
    TO=$2
    set -- `ec2metadata | grep instance-type`
    TYPE=$2
fi

if [ "$CLOUD" == "gce" ]; then
    set -- `gcutil getinstance $HOSTNAME | grep 'zone'`
    FROM=$4
    set -- `ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'gcutil getinstance $HOSTNAME | grep zone'`
    TO=$4
    set -- `gcutil getinstance $HOSTNAME | grep 'machine'`
    set -- `echo $4 | tr "/" " "`
    TYPE=$2
fi

LOG_FILE=$CLOUD-region-io-`date +"%Y-%m-%d-%H:%M:%S"-$FROM-$TO-$TYPE`
LOG=$LOG_DIR/$LOG_FILE

echo "# cross-region io benchmark" >> $LOG
echo `date +%s` >> $LOG
echo `date` >> $LOG

echo 'From:' >> $LOG
echo $FROM >> $LOG
echo 'To:' >> $LOG
echo $TO >> $LOG
echo 'Type:' >> $LOG
echo $TYPE >> $LOG

echo "File size:" >> $LOG
echo $FILE_SIZE >> $LOG

echo "netcat:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU" cat $SOURCE | nc $DEST_IP $NETCAT_PORT -q 0; } 2>>$LOG

echo "scp:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU" scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

echo "iperf:" >> $LOG
iperf -c $DEST_IP -p 12345 -t 60 | grep '/sec' >> $LOG

cd $LOG_DIR

git config --global user.name "Roma Koshel"
git config --global user.email "roman@scalr.com"
git add $LOG
git commit -m "$LOG_FILE"
git push -u origin master

ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 nc'
ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 iperf'
