#!/bin/bash
export SIMPLE_BACKUP_SUFFIX=ibf
for conf in CPU3D # GPU1D GPU3D CPU1D
do
  echo 'Generating code for ('$conf') target'
  rm -r $conf'_target'
  python2 GGDMLCompile.py -dsl io -sp $conf -ni src
  cd $conf'_target'
  indent -kr -nut -l1000  *.c *.h
  rm *.cibf *.hibf
  cd ..
done
