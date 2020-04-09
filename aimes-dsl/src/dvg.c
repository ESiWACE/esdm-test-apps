#include "grid.h"

extern GVAL EDGE 3D gv_grad;
extern GVAL CELL 3D gv_dvg;

void dvg(GRID* g)
{
    FOREACH cell IN grid
    {
        gv_dvg[cell] = 0;
        for(int n=0;n<NBRS;n++){
            gv_dvg[cell] += g->edge_weights[n][cell.cell %BLKSIZE] * gv_grad[cell.edge(n)];
        }
    }
}
