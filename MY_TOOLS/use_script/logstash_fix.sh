#!/bin/bash

home1=/data1/logstash
home2=/data/logstash
# 暂用logstash-zx.log路径判断
zxpath1=$home1/logstash-5.6.0/logs/logstash-zx.log
zxpath2=$home2/logstash-5.6.0/logs/logstash-zx.log
# 暂用 .sincedb 文件判断
sincepath1=$home1/.sincedb
sincepath2=$home2/.sincedb

logPath="/tmp/logstash/lgst"

if [ ! -d "$logPath" ]; then
  mkdir -p "$logPath"
fi

function killByName(){
  NAME=$1
  ID=`ps -ef | grep "$NAME" | grep -v "$0" | grep -v "grep" | awk '{print $2}'` # | grep -v fix 
  echo $ID
  for id in $ID
  do
    kill -9 $id
    echo "killed $id"
  done
}

function startLogst(){
  # home1=/data1/logstash
  home1=$1
  export LHOME=$home1/logstash-5.6.0 && $LHOME/bin/logstash -f $LHOME/config/dc-zx.conf -r -w 4 -b 1000 > $LHOME/logs/logstash-zx.log 2>&1
}

lessdef=0
timediff=0
lastRestart=0
if [ -f "$logPath/piddate" ]; then
  lastRestart=`date +%s -r $logPath/piddate`
fi

if [ -f "$zxpath1" ]; then
  # lessdef=`tail -n1000 $zxpath1 |grep -A3 sum|grep rate_1m|grep "e-"|wc -l`
  # lessdef=`tail -n1000 $zxpath1 |grep -A3 sum|grep rate_1m|tail -n1|grep '"rate_1m" => 0\.00'|wc -l`
  timediff=`date +%s -r $sincepath1`
elif [ -f "$zxpath2" ]; then
  # lessdef=`tail -n1000 $zxpath2 |grep -A3 sum|grep rate_1m|grep "e-"|wc -l`
  # lessdef=`tail -n1000 $zxpath2 |grep -A3 sum|grep rate_1m|tail -n1|grep '"rate_1m" => 0\.00'|wc -l`
  # TODO lessdef 正常情况下是看最后一行，
  timediff=`date +%s -r $sincepath2`
else
  lessdef=0
  timediff=`date +%s`
fi
nowt=`date +%s`
tdiff=`expr $nowt - $timediff`
udiff=`expr $nowt - $lastRestart`
echo $lessdef $timediff $tdiff $udiff >> $logPath/out

# if [ $lessdef -gt 1 ] && [ $tdiff -gt 300 ];then
if [ $tdiff -gt 240 ] && [ $tdiff -gt 540 ];then #4mis未更新且至少间隔 9 mins则重启
  if [ -f "$zxpath1" ]; then
    echo "killing hopme1" >> $logPath/out
    killByName $home1 >> $logPath/out
    echo $home1 > $logPath/piddate
    echo "home1 starting" >> $logPath/out
    startLogst $home1
  else
    echo "killing home2" >> $logPath/out
    killByName $home1 >> $logPath/out
    echo $home2 > $logPath/piddate
    echo "home2 starting" >> $logPath/out
    startLogst $home2
  fi
fi
