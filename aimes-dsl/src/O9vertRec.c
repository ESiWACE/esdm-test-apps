#include "grid.h"
extern GVAL CELL 3D gv_temp;
extern GVAL CELL 3D gv_dvg;
extern GVAL CELL 3D gv_o9var;
extern GVAL*restrict*restrict tmpVR;

void O9vertRec(GRID* g)
{
    FOREACH cell IN grid|height{0..0}
    {
        tmpVR[0][cell.cell] = gv_dvg[cell];
        gv_o9var[cell] = gv_temp[cell];
    }

    FOREACH cell IN grid|height{1..g->height}
    {
        tmpVR[cell.height][cell.cell] = gv_dvg[cell] + gv_dvg[cell.below()];
        gv_o9var[cell] = 0.5 * (gv_temp[cell] + gv_temp[cell.below()]) + 0.05 * tmpVR[cell.height-1][cell.cell];
    }
}
