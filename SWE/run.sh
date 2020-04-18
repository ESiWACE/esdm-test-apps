#!/bin/bash
source ../source.sh

checkCFG

mkesdm
echo To run with NetCDF, use:
echo mpiexec -np 2 ./build/SWE_gnu_release_mpi_fwave.nc -x 1024 -y 1024 -o "esdm://test" -c 2
echo To run with ESDM, use:
echo mpiexec -np 2 ./build/SWE_gnu_release_mpi_fwave.esdm -x 1024 -y 1024 -o "test" -c 2
