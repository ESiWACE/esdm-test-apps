#include "grid.h"
extern GVAL EDGE 3D gv_grad;
extern GVAL *restrict*restrict*restrict gv_precInd;
extern int *restrict t7Blk;
extern int *restrict t7Ind;

void O7precIndxNb(GRID* g)
{
    FOREACH edge IN grid
    {
        int jb=t7Blk[edge.block * g->blkSize + edge.edge],
            je=t7Ind[edge.block * g->blkSize + edge.edge];
        gv_precInd[jb][edge.height][je] = 0.5 * gv_grad[edge];
    }
}
