#！/bin/bash

size=72000
#size=10
for ((i=0; i<25; i++))
do
  offset=`expr $i \* $size`
  echo $offset $size
  python extract_ner_script.py $i $offset $size &
done

# ps -aux | grep test | grep -v grep | awk '{print $2}' | xargs kill -9