#include "grid.h"

extern GVAL CELL 3D gv_temp;
extern GVAL EDGE 3D gv_grad;

void grad(GRID* g)
{
    FOREACH edge IN grid
    {
            gv_grad[edge] = gv_temp[edge.cell(0)] - gv_temp[edge.cell(1)];
    }
}
