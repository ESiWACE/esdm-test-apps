#include "grid.h"
#include "memory.h"
#include "component.h"
#include "io.h"
#include <stdint.h>

void com3_init(GRID* g);
void com3_compute(GRID* g);
void com3_io(GRID* g);
double com3_flops(GRID* g);
double com3_memory(GRID* g);
uint64_t com3_checksum(GRID*);
void com3_cleanup(GRID* g);

void O2VertIntegration(GRID* g);
void O3Indirect2D(GRID* g);
void O4Indirect3D(GRID* g);
void O5Indirect3D(GRID* g);

GVAL CELL 2D gv_vi;
GVAL EDGE 2D gv_ind2Dparam;
GVAL EDGE 3D gv_ind2Dvar;
GVAL EDGE 3D gv_ind3Dvar;
int EDGE 3D t3DBlk;
int EDGE 3D t3DIdx;
int EDGE 3D t3DVer;

io_var_t io_gv_vi;
io_var_t io_gv_ind2Dvar;
io_var_t io_gv_ind3Dvar;

MODEL_COMPONENT com3={
    0,
    com3_init,
    com3_compute,
    com3_io,
    com3_flops,
    com3_memory,
    com3_checksum,
    com3_cleanup
};

extern GVAL EDGE 3D gv_grad;
void init_opO4(GRID* g)
{
    ALLOC t3DBlk;
    ALLOC t3DIdx;

    FOREACH edge IN grid
    {
        if(gv_grad[edge]>0){
            t3DBlk[edge] = edge.cell(0).block;
            t3DIdx[edge] = edge.cell(0).cell;
        }
        else
        {
            t3DBlk[edge] = edge.cell(1).block;
            t3DIdx[edge] = edge.cell(1).cell;
        }
    }
}

void init_opO5(GRID* g)
{
    ALLOC t3DVer;

    FOREACH edge IN grid|height{0..(g->height-2)}
    {
        t3DVer[edge] = edge.height + 1;
    }
    FOREACH edge IN grid|height{(g->height-1)..(g->height-1)}
    {
        t3DVer[edge] = (g->height-1);
    }
}


extern MODEL_COMPONENT com1;
void com3_init(GRID* g)
{
    com3.loaded = 1;
    if(!com1.loaded)com1.init(g);
    ALLOC gv_vi;
    ALLOC gv_ind2Dparam;
    ALLOC gv_ind2Dvar;
    ALLOC gv_ind3Dvar;
    init_opO4(g);
    init_opO5(g);

    io_read_register(g, "gv_ind2Dparam", (GVAL *)gv_ind2Dparam, FLOAT32, FLOAT32,
		     GRID_POS_EDGE, GRID_DIM_2D);

    io_write_define(g, "gv_vi", (GVAL *)gv_vi, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_2D, &io_gv_vi);
    io_write_define(g, "gv_ind2Dvar", (GVAL *)gv_ind2Dvar, FLOAT32,
		    GRID_POS_EDGE, GRID_DIM_3D, &io_gv_ind2Dvar);
    io_write_define(g, "gv_ind3Dvar", (GVAL *)gv_ind3Dvar, FLOAT32,
		    GRID_POS_EDGE, GRID_DIM_3D, &io_gv_ind3Dvar);
}

void com3_compute(GRID* g)
{
    O2VertIntegration(g);
    O3Indirect2D(g);
    O4Indirect3D(g);
    O5Indirect3D(g);
}

void com3_io(GRID* g){
    io_write_announce(g, &io_gv_vi);
    io_write_announce(g, &io_gv_ind2Dvar);
    io_write_announce(g, &io_gv_ind3Dvar);
}

double com3_flops(GRID* g)
{
    double flop = (double)g->cellCount * (double)g->height
            + 3.0 * (double)g->edgeCount * (double)g->height
            + (double)g->edgeCount * (double)g->height;
    return flop;
}

double com3_memory(GRID* g)
{
    double mem = ((double)g->cellCount
                + (double)g->edgeCount
                + (double)g->edgeCount * (double)g->height
                + (double)g->edgeCount * (double)g->height)
                *(double)sizeof(GVAL)
                + (3.0 * (double)g->edgeCount * (double)g->height)
                *(double)sizeof(int);
    return mem/(1024*1024);
}

uint64_t com3_checksum(GRID* g)
{
    uint64_t ret = 0;
    FOREACH cell IN gridCELL2D
    {
            ret += (uint64_t)gv_vi[cell];
    }
    FOREACH edge IN grid
    {
            ret += (uint64_t)gv_ind2Dvar[edge];
            ret += (uint64_t)gv_ind3Dvar[edge];
    }
    return ret;  
}

void com3_cleanup(GRID* g)
{
    com3.loaded = 0;
    DEALLOC gv_vi;
    DEALLOC gv_ind2Dparam;
    DEALLOC gv_ind2Dvar;
    DEALLOC gv_ind3Dvar;
    DEALLOC t3DBlk;
    DEALLOC t3DIdx;
    DEALLOC t3DVer;
}
