#include "grid.h"
extern GVAL CELL 3D gv_temp;
extern GVAL EDGE 3D gv_ind3Dvar;
int EDGE 3D t3DBlk;
int EDGE 3D t3DIdx;




void O4Indirect3D(GRID* g)
{
    FOREACH edge IN grid
    {
            gv_ind3Dvar[edge] = 0;
    }
}
