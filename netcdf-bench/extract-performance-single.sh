#!/bin/bash

function extract(){
  t=$1
  f=$2

  for p in $(grep "$t *I/O Performance  " $f | cut -b "62-80") ; do
    echo -n $(basename $f | sed 's/\(.*\)-\([^-]*\)-\([^-]*\).txt/\1 \2 \3/') | sed "s/.conf//"
    echo " $t $p"
  done
}

for f in $@ ; do
  extract write $f
  extract read $f
done
