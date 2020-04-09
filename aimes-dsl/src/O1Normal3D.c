#include "grid.h"

extern GVAL CELL 3D gv_temp;
extern GVAL CELL 3D gv_dvg;

void O1Normal3D(GRID* g)
{
    FOREACH cell IN grid
    {
        gv_temp[cell] += 0.05 * gv_dvg[cell];
    }
}
