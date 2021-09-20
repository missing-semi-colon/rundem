#!/bin/sh

echo "Counting to 10..."
sleep 0.5
num=0
while [ $num -lt 11 ]
do
	sleep 0.2
	echo "$num"
	num=$(($num+1))
done
