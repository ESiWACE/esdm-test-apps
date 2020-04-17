#include "grid.h"
#include "memory.h"
#include "component.h"
#include "io.h"
#include <stdint.h>

void com4_init(GRID* g);
void com4_compute(GRID* g);
void com4_io(GRID* g);
double com4_flops(GRID* g);
double com4_memory(GRID* g);
uint64_t com4_checksum(GRID*);
void com4_cleanup(GRID* g);

void grad(GRID*g);
void O6precIndxDb(GRID* g);
void O7precIndxNb(GRID* g);
void O8ind(GRID* g);

GVAL *restrict *restrict *restrict gv_precInd;
int *restrict t6Blk;
int *restrict t6Ver;
int *restrict t6Ind;
int *restrict t7Blk;
int *restrict t7Ind;
GVAL CELL 2D gv_o8param[3];
GVAL CELL 3D gv_o8par2;
GVAL CELL 3D gv_o8var;

io_var_t io_gv_precInd;
io_var_t io_gv_o8var;

MODEL_COMPONENT com4={
    0,
    com4_init,
    com4_compute,
    com4_io,
    com4_flops,
    com4_memory,
    com4_checksum,
    com4_cleanup
};

void init_opO6(GRID* g)
{
    t6Blk = malloc((g->eBlkCnt*g->height*g->blkSize)*sizeof(int));
    t6Ver = malloc((g->eBlkCnt*g->height*g->blkSize)*sizeof(int));
    t6Ind = malloc((g->eBlkCnt*g->height*g->blkSize)*sizeof(int));

    FOREACH edge IN grid
    {
        t6Blk[edge.block*g->height*g->blkSize+edge.height*g->blkSize+edge.edge] = edge.block;
        t6Ver[edge.block*g->height*g->blkSize+edge.height*g->blkSize+edge.edge] = edge.height;
        t6Ind[edge.block*g->height*g->blkSize+edge.height*g->blkSize+edge.edge] = edge.edge;
    }

    int eb,ee;
    #pragma omp parallel for
    for(int b=0;b<g->eBlkCnt;b++){
        get_indices_e(g,b,&eb,&ee);
        for(int k=0;k<g->height;k++){
            for(int e=eb;e<ee;e++){
                t6Blk[b*g->height*g->blkSize+k*ee+e] = b;
                t6Ver[b*g->height*g->blkSize+k*ee+e] = k;
                t6Ind[b*g->height*g->blkSize+k*ee+e] = e;
            }
        }
    }
}

void init_opO7(GRID* g)
{
    t7Blk = malloc((g->edgeCount)*sizeof(int));
    t7Ind = malloc((g->edgeCount)*sizeof(int));

    FOREACH edge IN gridEDGE2D
    {
        t7Blk[edge.block*g->blkSize+edge.edge] = edge.block;
        t7Ind[edge.block*g->blkSize+edge.edge] = edge.edge;
    }
}

extern MODEL_COMPONENT com1;
void com4_init(GRID* g)
{
    com4.loaded = 1;
    if(!com1.loaded)com1.init(g);
    gv_precInd = (GVAL *restrict *restrict *restrict)allocate_variable(g, GRID_POS_EDGE, GRID_DIM_3D, sizeof(GVAL));
    init_opO6(g);
    init_opO7(g);
    for(int i=0;i<3;i++)
        ALLOC gv_o8param[i];
    ALLOC gv_o8par2;
    ALLOC gv_o8var;

    io_read_register(g, "gv_o8param0", (GVAL *)gv_o8param[0], FLOAT32, FLOAT32,
		     GRID_POS_CELL, GRID_DIM_2D);
    io_read_register(g, "gv_o8param1", (GVAL *)gv_o8param[1], FLOAT32, FLOAT32,
		     GRID_POS_CELL, GRID_DIM_2D);
    io_read_register(g, "gv_o8param2", (GVAL *)gv_o8param[2], FLOAT32, FLOAT32,
		     GRID_POS_CELL, GRID_DIM_2D);

    io_read_register(g, "gv_o8par2", (GVAL *)gv_o8par2, FLOAT32, FLOAT32,
		     GRID_POS_CELL, GRID_DIM_3D);

    io_write_define(g, "gv_precInd", (GVAL *)gv_precInd, FLOAT32,
		    GRID_POS_EDGE, GRID_DIM_3D, &io_gv_precInd);
    io_write_define(g, "gv_o8var", (GVAL *)gv_o8var, FLOAT32,
		    GRID_POS_CELL, GRID_DIM_3D, &io_gv_o8var);
}

void com4_compute(GRID* g)
{
    grad(g);
    O6precIndxDb(g);
    O7precIndxNb(g);
    O8ind(g);
}

void com4_io(GRID* g){
    io_write_announce(g, &io_gv_precInd);
    io_write_announce(g, &io_gv_o8var);
}

double com4_flops(GRID* g)
{
    double flop = (double)g->edgeCount * (double)g->height
            + (double)g->edgeCount * (double)g->height
            + (double)g->edgeCount * (double)g->height
            + 14.0 * (double)g->cellCount * (double)(g->height-1) + 20.0 * (double)g->cellCount;
    return flop;
}

double com4_memory(GRID* g)
{
    double mem = ((double)g->edgeCount*(double)g->height
                + 3.0 * (double)g->cellCount
                + (double)g->cellCount * (double)g->height
                + (double)g->cellCount * (double)g->height)
                *(double)sizeof(GVAL)
                + (3.0 * (double)g->eBlkCnt * (double)g->height * (double)g->blkSize
                + 2.0 * (double)g->edgeCount)
                *(double)sizeof(int);
    return mem/(1024*1024);
}

uint64_t com4_checksum(GRID* g)
{
    uint64_t ret = 0;
    FOREACH cell IN grid
    {
            ret += (uint64_t)gv_o8var[cell];
    }
    return ret;
}

void com4_cleanup(GRID* g)
{
    io_cleanup(& io_gv_o8var);
    io_cleanup(& io_gv_precInd);

    com4.loaded = 0;
    deallocate_variable((void*)gv_precInd, g, GRID_POS_EDGE, GRID_DIM_3D, sizeof(GVAL));
    free((void*)t6Blk);
    free((void*)t6Ver);
    free((void*)t6Ind);
    free((void*)t7Blk);
    free((void*)t7Ind);
    for(int i=0;i<3;i++)
        DEALLOC gv_o8param[i];
    DEALLOC gv_o8par2;
    DEALLOC gv_o8var;
}
