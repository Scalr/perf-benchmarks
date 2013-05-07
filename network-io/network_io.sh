#!/bin/bash

SSH_KEY=$1
USER=$2
DEST_IP=$3
NETCAT_PORT=$4
FILE_SIZE=$5
CLOUD=$6
SOURCE=/tmp/io_benchmarks
DEST=/dev/null
RES_DIR=$HOME/perf-benchmarks/network-io/results

if [ "$CLOUD" == "ec2" ]; then
    set -- `ec2metadata | grep availability-zone`
    FROM=$2
    set -- `ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'ec2metadata | grep availability-zone'`
    TO=$2
    set -- `ec2metadata | grep instance-type`
    TYPE=$2
elif [ "$CLOUD" == "gce" ]; then
    set -- `gcutil getinstance $HOSTNAME | grep 'zone'`
    FROM=$4
    set -- `ssh -i $HOME/.ssh/id_rsa -l $USER $DEST_IP 'gcutil getinstance $HOSTNAME | grep zone'`
    TO=$4
    set -- `gcutil getinstance $HOSTNAME | grep 'machine'`
    set -- `echo $4 | tr "/" " "`
    TYPE=$2
else
    CLOUD="unknown"
    FROM="unknown"
    TO="unknown"
    TYPE="unknown"
fi

LOG_DIR=$RES_DIR/$CLOUD/$TYPE

if [ ! -d $LOG_DIR ]; then
    mkdir -p $LOG_DIR
fi

LOG_NAME=`date +"%Y-%m-%d-%H:%M:%S"`-network-io-$FROM-$TO
LOG=$LOG_DIR/$LOG_NAME

echo "# network-io" >> $LOG
echo `date +%s` >> $LOG
echo `date -u` >> $LOG

echo 'From:' >> $LOG
echo $FROM >> $LOG
echo 'To:' >> $LOG
echo $TO >> $LOG
echo 'Type:' >> $LOG
echo $TYPE >> $LOG

echo "File size:" >> $LOG
echo $FILE_SIZE >> $LOG

truncate -s $FILE_SIZE $SOURCE

echo "netcat ..."
echo "netcat:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory" cat $SOURCE | nc $DEST_IP $NETCAT_PORT -q 0; } 2>>$LOG

echo "scp ..."
echo "scp:" >> $LOG
{ /usr/bin/time -f "%E Elapsed\n%U User\n%S System\n%M Memory" scp -i $SSH_KEY $SOURCE $USER@$DEST_IP:$DEST 1>/dev/null ; } 2>>$LOG

echo "iperf ..."
echo -e "\tstarting server ..."
ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 iperf &>/dev/null'
ssh -i $SSH_KEY -l $USER $DEST_IP 'iperf -s -p 12345 &>/dev/null &' &

sleep 1

echo -e "\tsimple mode ..."
echo "iperf simple mode:" >> $LOG
iperf -c $DEST_IP -p 12345 -t 30 | grep '/sec' >> $LOG

echo -e "\tdualtest mode ..."
echo "iperf dualtest:" >> $LOG
iperf -c $DEST_IP -p 12345 -t 30 -d | grep '/sec' >> $LOG

echo -e "\tparallel mode 4 ..."
echo "iperf parallel mode 4:" >> $LOG
iperf -c $DEST_IP -p 12345 -t 30 -P 4 | grep '/sec' >> $LOG

cd $LOG_DIR

echo "committing  results ..."
git fetch origin
git pull origin master
git add $LOG
git commit -m "$CLOUD $TYPE $LOG_NAME"
git push -u origin master

ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 nc &>/dev/null' &>/dev/null
ssh -i $SSH_KEY -l $USER $DEST_IP 'sudo killall -9 iperf &>/dev/null' &>/dev/null

echo "done"

