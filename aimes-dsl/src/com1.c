#include "grid.h"
#include "memory.h"
#include "component.h"
#include "io.h"

#include <stdint.h>

void com1_init(GRID* g);
void com1_compute(GRID* g);
void com1_io(GRID* g);
double com1_flops(GRID* g);
double com1_memory(GRID* g);
uint64_t com1_checksum(GRID*);
void com1_cleanup(GRID* g);

void grad(GRID*g);
void dvg(GRID*g);
void step(GRID*g);

GVAL CELL 3D gv_temp;
GVAL EDGE 3D gv_grad;
GVAL CELL 3D gv_dvg;

static io_var_t io_gv_temp;
static io_var_t io_gv_grad;
static io_var_t io_gv_dvg;

MODEL_COMPONENT com1={
    0,
    com1_init,
    com1_compute,
    com1_io,
    com1_flops,
    com1_memory,
    com1_checksum,
    com1_cleanup
};

void com1_init(GRID* g)
{
    com1.loaded = 1;
    ALLOC gv_temp;
    ALLOC gv_grad;
    ALLOC gv_dvg;

    io_read_register(g, "gv_temp", (GVAL *)gv_temp, FLOAT32, FLOAT32, GRID_POS_CELL, GRID_DIM_3D);

    io_write_define(g, "gv_temp", (GVAL *)gv_temp, FLOAT32, GRID_POS_CELL, GRID_DIM_3D, &io_gv_temp);
    io_write_define(g, "gv_grad", (GVAL *)gv_grad, FLOAT32, GRID_POS_EDGE, GRID_DIM_3D, &io_gv_grad);
    io_write_define(g, "gv_dvg",  (GVAL *)gv_dvg,  FLOAT32, GRID_POS_CELL, GRID_DIM_3D, &io_gv_dvg);
}

void com1_compute(GRID* g)
{
    grad(g);
    dvg(g);
    step(g);
}

void com1_io(GRID* g){
    io_write_announce(g, &io_gv_grad);
    io_write_announce(g, &io_gv_dvg);
}

double com1_flops(GRID* g)
{
    double flop = (double)g->edgeCount * (double)g->height
                + 2.0 * (double)NBRS * (double)g->cellCount * (double)g->height
                + 2.0 * (double)g->cellCount * (double)g->height;
    return flop;
}

double com1_memory(GRID* g)
{
    double mem = ((double)g->edgeCount * (double)g->height
                + 2.0 * (double)g->cellCount * (double)g->height)
              *sizeof(GVAL);
    return mem/(1024*1024);
}

uint64_t com1_checksum(GRID* g)
{
    uint64_t ret = 0;
    FOREACH cell IN grid
    {
            ret += (uint64_t)gv_temp[cell];
            ret += (uint64_t)gv_dvg[cell];
    }
    FOREACH edge IN grid
    {
            ret += (uint64_t)gv_grad[edge];
    }
    return ret;
}

void com1_cleanup(GRID* g)
{
    io_cleanup(& io_gv_temp);
    io_cleanup(& io_gv_grad);
    io_cleanup(& io_gv_dvg);

    com1.loaded = 0;
    DEALLOC gv_temp;
    DEALLOC gv_grad;
    DEALLOC gv_dvg;
}
