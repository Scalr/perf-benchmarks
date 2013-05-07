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
LOG_FILE=region-io-`date +"%Y-%m-%d-%H:%M:%S"`
LOG=$LOG_DIR/$LOG_FILE

if [ ! -d $LOG_DIR ]; then
    mkdir $LOG_DIR
fi

truncate -s $FILE_SIZE $SOURCE

echo "# cross-region io benchmark" >> $LOG
echo `date +%s` >> $LOG
echo `date` >> $LOG

if [ "$CLOUD" == "ec2" ]; then
    set -- `ec2metadata | grep availability-zone`
    FROM=$2
    set -- ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'ec2metadata | grep availability-zone'
    TO=$2
    set -- `ec2metadata | grep instance-type`
    TYPE=$2
    echo 'From:' >> $LOG
    $FROM >> $LOG
    echo 'To:' >> $LOG
    $TO >> $LOG
    echo 'Type:' >> $LOG
    $TYPE >> $LOG
fi

if [ "$CLOUD" == "gce" ]; then
    echo 'From:' >> $LOG
    echo `gcutil getinstance $HOSTNAME | grep 'zone'` >> $LOG
    echo 'To:' >> $LOG
    ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'gcutil getinstance $HOSTNAME | grep zone' >> $LOG
    echo 'Type:' >> $LOG
    echo `gcutil getinstance $HOSTNAME | grep 'machine'` >> $LOG
fi

echo "File size:" >> $LOG
echo $FILE_SIZE >> $LOG

echo "netcat:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU" cat $SOURCE | nc $DEST_IP $NETCAT_PORT -q 0; } 2>>$LOG

echo "scp:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory\n%P Percentage of the CPU" scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST; } 2>>$LOG

echo "iperf:" >> $LOG
iperf -c $DEST_IP -p 12345 -t 60 | grep '/sec' >> $LOG

cd $LOG_DIR
mv $LOG_FILE $LOG_FILE-$FROM-$TO-$TYPE

git config --global user.name "Roma Koshel"
git config --global user.email "roman@scalr.com"
git add $LOG
git commit -m "$LOG_FILE-$FROM-$TO-$TYPE"
git push -u origin master

ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 nc'
ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 iperf'
