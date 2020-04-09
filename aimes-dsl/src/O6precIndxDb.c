#include "grid.h"
extern GVAL EDGE 3D gv_grad;
extern GVAL *restrict*restrict*restrict gv_precInd;
extern int *restrict t6Blk;
extern int *restrict t6Ver;
extern int *restrict t6Ind;



void O6precIndxDb(GRID* g)
{
    FOREACH edge IN grid
    {
        int i = edge.block * g->height * g->blkSize + edge.height * g->blkSize + edge.edge;
        gv_precInd[t6Blk[i]][t6Ver[i]][t6Ind[i]] = 0.5 * gv_grad[edge];
    }
}
