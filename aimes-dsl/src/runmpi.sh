#!/bin/bash
DTYPE=float
BLOCK=64
TILE=3
echo "using $TILE-side tiled grid (Data type: $DTYPE, Block size: $BLOCK)"
mpicc *.c -o a.out -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -lnetcdf -I/home/nabeeh/Desktop/tmp/netcdf-4.1.3/include # -fopenmp
mpiexec -n 1  --map-by node --display-map  ./a.out -G=1024 -m=0 -M=1000 -T=10 -R=input.cdf -W=output.cdf
#mpiexec -n 1  --map-by node --display-map  ./a.out -G=256 -m=0 -M=1000 -T=10 -R=test_gv_temp2 -W=output.cdf

