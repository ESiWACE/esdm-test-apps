#include "grid.h"

extern GVAL CELL 3D gv_temp;
extern GVAL CELL 2D gv_vi;

void O2VertIntegration(GRID* g)
{
    FOREACH cell IN grid
    {
        gv_vi[cell] += gv_temp[cell];
    }
}
