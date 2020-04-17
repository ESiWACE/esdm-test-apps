#!/bin/bash -e
source ../../source.sh

DTYPE=float
BLOCK=64
TILE=3
GRID=1024
echo "using $TILE-side tiled grid (Data type: $DTYPE, Block size: $BLOCK)"

cp ../../esdm.conf .

echo "Creating input file"
mpicc tools/var_init.c option.c io_netcdf.c grid.c -o var_init -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 $CFLAGS $LDFLAGS -lnetcdf

mkesdm
./var_init -G=$GRID -f=esdm://input.cdf

mpicc *.c -o model.nc -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -fopenmp $CFLAGS $LDFLAGS -lnetcdf
echo "Building with ESDM"
mpicc *.c -DUSE_ESDM -o model-esdm -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -fopenmp $CFLAGS $LDFLAGS -lnetcdf

echo "To run the model, use (model.nc or model.esdm)"
echo mpiexec -n 2 --map-by node --display-map  ./model.XXX -G=$GRID -m=0 -M=1000 -T=10 -R=esdm://input.cdf -W=esdm://output.cdf
