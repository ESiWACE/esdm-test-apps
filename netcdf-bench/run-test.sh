#!/bin/bash

source ../source.sh

mkfs.esdm -g -l --create --remove --ignore-errors
./benchtool -f=esdm://longtest -w -r

mkfs.esdm -g -l --create --remove --ignore-errors
mpiexec -np 2 ./benchtool -f="esdm://test.esdm" -n=1 -p=2


echo "Cleanup"
rm -rf _metadummy _esdm

echo "[OK]"
