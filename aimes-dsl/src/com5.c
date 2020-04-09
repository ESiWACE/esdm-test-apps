#include "grid.h"
#include "memory.h"
#include "component.h"
#include "io.h"
#include <stdint.h>

void com5_init(GRID* g);
void com5_compute(GRID* g);
void com5_io(GRID* g);
double com5_flops(GRID* g);
double com5_memory(GRID* g);
uint64_t com5_checksum(GRID*);
void com5_cleanup(GRID* g);

void lap(GRID*g);

GVAL CELL 3D gv_temp_alt;

MODEL_COMPONENT com5={
    0,
    com5_init,
    com5_compute,
    com5_io,
    com5_flops,
    com5_memory,
    com5_checksum,
    com5_cleanup
};

extern MODEL_COMPONENT com1;
void com5_init(GRID* g)
{
    com5.loaded = 1;
    if(!com1.loaded)com1.init(g);
    ALLOC gv_temp_alt;
}

void com5_io(GRID *g)
{

}

void com5_compute(GRID* g)
{
    lap(g);
}

double com5_flops(GRID* g)
{
    double flop = 59.0 * (double)g->cellCount * (double)(g->height-2);
    return flop;
}

double com5_memory(GRID* g)
{
    return 0.0;
}

uint64_t com5_checksum(GRID* g)
{
    return 0;  
}

void com5_cleanup(GRID* g)
{
    DEALLOC gv_temp_alt;
}
