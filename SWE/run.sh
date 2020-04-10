#!/bin/bash
source ../source.sh

mkesdm
mpiexec -np 2 ./build/SWE_gnu_release_mpi_fwave -x 1024 -y 1024 -o "esdm://test" -c 2
