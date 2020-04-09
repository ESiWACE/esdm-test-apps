#!/bin/bash
DTYPE=float
BLOCK=64
TILE=3
mpicc tools/var_init.c option.c io_netcdf.c grid.c -o var_init.out -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -lnetcdf -I/home/nabeeh/Desktop/tmp/netcdf-4.1.3/include
mpiexec -n 1 var_init.out -G=1024 -f=input.cdf
