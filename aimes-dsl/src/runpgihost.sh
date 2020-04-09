#!/bin/bash
DTYPE=float
BLOCK=1024
TILE=3
echo "using $TILE-side tiled grid (Data type: $DTYPE, Block size: $BLOCK)"
pgcc *.c -o a.out -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -mp -Minline
./a.out -G=2048 -m=2 -M=5

