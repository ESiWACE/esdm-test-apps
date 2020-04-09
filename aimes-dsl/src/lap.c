#include "grid.h"

extern GVAL CELL 3D  gv_temp;
extern GVAL CELL 3D  gv_temp_alt;

void lap(GRID* g)
{
    FOREACH cell IN grid
    {
        gv_temp_alt[cell] = (gv_temp[cell.neighbor(0)] + gv_temp[cell.neighbor(1)] + gv_temp[cell.neighbor(2)])/3.0;
    }
    GVAL CELL 3D  x=gv_temp_alt;
    gv_temp_alt=gv_temp;
    gv_temp=x;
}
