#!/bin/bash
DTYPE=float
BLOCK=2048
TILE=3
echo "using $TILE-side tiled grid (Data type: $DTYPE, Block size: $BLOCK)"
pgcc *.c -o a.out -DGVAL=$DTYPE -DNBRS=$TILE -DBLKSIZE=$BLOCK -O3 -acc -ta=tesla:managed -Minline
./a.out -G=256 -m=2 -M=5

