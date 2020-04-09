#include "grid.h"

extern GVAL CELL 3D  gv_temp;
extern GVAL CELL 3D gv_dvg;

void step(GRID* g)
{
    FOREACH cell IN grid
    {
        gv_temp[cell] += 0.1 * gv_dvg[cell];
    }
}
