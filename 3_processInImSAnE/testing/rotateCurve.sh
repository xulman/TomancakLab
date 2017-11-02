#!/bin/bash

if [ $# -lt 2 ]; then
	echo "Expect two params: input_file output_file"
	exit 0
fi

# init output file
cat /dev/null > $2

# line counters
L=`cat $1 | wc -l`
l=1;

# rotate...
while [ $l -le $L ]; do
	tail -n $l $1 | head -1 >> $2
	l=$((l+1));
done
