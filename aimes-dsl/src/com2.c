#include "grid.h"
#include "memory.h"
#include "component.h"
#include "io.h"
#include <stdint.h>

void com2_init(GRID* g);
void com2_compute(GRID* g);
void com2_io(GRID* g);
double com2_flops(GRID* g);
double com2_memory(GRID* g);
uint64_t com2_checksum(GRID*);
void com2_cleanup(GRID* g);

void grad(GRID*g);
void dvg(GRID*g);
void O1Normal3D(GRID* g);
void O9vertRec(GRID* g);
void O10BlkRed(GRID* g);

GVAL CELL 3D gv_o9var;
GVAL *restrict*restrict tmpVR;
char *restrict levelMask;
char *restrict*restrict levMsk;
GVAL *restrict vcflMax;
GVAL vcflMaxVal = 0.0;

io_var_t io_gv_o9var;

MODEL_COMPONENT com2={
    0,
    com2_init,
    com2_compute,
    com2_io,
    com2_flops,
    com2_memory,
    com2_checksum,
    com2_cleanup
};

void init_opO9(GRID* g)
{
    tmpVR = malloc(g->height*sizeof(GVAL*));
    for(int k=0;k<g->height;k++){
        tmpVR[k] = malloc(g->blkSize*sizeof(GVAL));
    }
}

void init_op10(GRID* g)
{
    levelMask = malloc(g->height*sizeof(char));
    levMsk = malloc(g->cBlkCnt*sizeof(char*));
    vcflMax = malloc(g->cBlkCnt*sizeof(GVAL));

    for(int b=0;b<g->cBlkCnt;b++){
        levMsk[b] = malloc(g->height*sizeof(char));
        vcflMax[b] = 0.0;
        for(int k=0;k<g->height;k++){
            levMsk[b][k] = 0;
        }
    }
    for(int k=0;k<g->height;k++){
        levelMask[k] = 0;
    }
}

extern MODEL_COMPONENT com1;
void com2_init(GRID* g)
{
    com2.loaded = 1;
    if(!com1.loaded)com1.init(g);
    ALLOC gv_o9var;
    init_opO9(g);
    init_op10(g);

    io_write_define(g, "gv_o9var", (GVAL *)gv_o9var, FLOAT32, GRID_POS_CELL, GRID_DIM_3D, &io_gv_o9var);
}
void com2_compute(GRID* g)
{
    grad(g);
    dvg(g);
    O1Normal3D(g);
    O9vertRec(g);
    O10BlkRed(g);
}

void com2_io(GRID* g){
    io_write_announce(g, &io_gv_o9var);
}

double com2_flops(GRID* g)
{
    double flop = (double)g->edgeCount * (double)g->height
                + (double)NBRS * 2.0 * (double)g->cellCount * (double)g->height
                + 2.0 * (double)g->cellCount * (double)g->height
                + 5.0 * (double)g->cellCount * (double)(g->height-1);
    return flop;
}

double com2_memory(GRID* g)
{
    double mem = ((double)g->cellCount*(double)g->height
                + (double)g->blkSize * (double)g->height
                + (double)g->cBlkCnt * (double)g->height
                + (double)g->cBlkCnt
                + (double)g->height)
                *(double)sizeof(GVAL);
    return (double)mem/(1024*1024);
}

uint64_t com2_checksum(GRID* g)
{
    uint64_t ret = 0;
    return ret;
}

void com2_cleanup(GRID* g)
{
    io_cleanup(& io_gv_o9var);

    com2.loaded = 0;
    DEALLOC gv_o9var;
    for(int k=0;k<g->height;k++){
        free((void*)(tmpVR[k]));
    }
    free((void*)tmpVR);

    free((void*)levelMask);
    for(int b=0;b<g->cBlkCnt;b++){
        free((void*)(levMsk[b]));
    }
    free((void*)levMsk);
    free((void*)vcflMax);

}
