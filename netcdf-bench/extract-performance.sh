#!/bin/bash

function extract(){
  t=$1
  f=$2

  echo -n $(basename $f | sed 's/\(.*\)-\([^-]*\)-\([^-]*\).txt/\1 \2 \3/') | sed "s/.conf//"
  echo -n " $t "
  echo -n "("
  echo -n $(grep "$t *I/O Performance  " $f | cut -b "62-80") | sed "s/ / + /g"
  echo    ")/"
}

for f in $@ ; do
  extract read $f
done

for f in $@ ; do
  extract write $f
done
