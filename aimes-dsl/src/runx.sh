#!/bin/bash
DTYPE=float
BLOCK=128
TILE=3
echo "using $TILE-side tiled grid (Data type: $DTYPE, Block size: $BLOCK)"
gcc *.c -o a.out -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -fopenmp
./a.out -G=256 -m=2 -M=5
