#ifndef GRID_H
#define GRID_H

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define GVAL float
#define NBRS 3
//#define BLKSIZE 4

typedef struct {
    int i;
    int j;
} map_t;

typedef struct {
    int cellCount;
    int height;
    int edgeCount;
    int blkSize;
    int cBlkCnt;
    int eBlkCnt;
    
    
    int *restrict neighbor[NBRS];
    int CELL 2D cNeighborIdx[NBRS];
    int CELL 2D cNeighborBlk[NBRS];
    
    int *restrict cedge[NBRS];
    int CELL 2D cEdgeIdx[NBRS];
    int CELL 2D cEdgeBlk[NBRS];
    
    int *restrict ecell[2];
    int EDGE 2D eCellIdx[2];
    int EDGE 2D eCellBlk[2];
    
    int *restrict*restrict map1;//in fact no need to keep
    map_t * restrict map2;
    
    GVAL edge_weights[NBRS][BLKSIZE];
    int mpi_world_size;
    int mpi_rank;
} GRID;

void init_grid(GRID* g, int cellCount, int height);
void get_indices_c(GRID* g, int blk, int* cb, int* ce);
void get_indices_e(GRID* g, int blk, int* eb, int* ee);

#endif
