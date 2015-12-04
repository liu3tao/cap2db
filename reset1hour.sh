#!/bin/sh
i=1
while [ i ]
do
	echo "hehe"
	python cap2csv-live.py mon0 52.89.72.172:8086 pi_suny_1 > /dev/null
	sleep 1
	rm -rf /tmp/wireshark*
	sleep 1
done
