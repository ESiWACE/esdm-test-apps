#include "grid.h"

extern GVAL CELL 3D gv_temp;
extern GVAL CELL 2D gv_ind2Dparam;
extern GVAL EDGE 3D gv_ind2Dvar;

void O3Indirect2D(GRID* g)
{
    FOREACH edge IN grid
    {
            gv_ind2Dvar[edge] = gv_ind2Dparam[edge.cell(0)] * gv_temp[edge.cell(0)]
                - gv_ind2Dparam[edge.cell(1)] * gv_temp[edge.cell(1)];
    }
}
