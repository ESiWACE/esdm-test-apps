#include "grid.h"
extern GVAL EDGE 3D gv_grad;
extern GVAL CELL 2D gv_o8param[3];
extern GVAL CELL 3D gv_o8par2;
extern GVAL CELL 3D gv_o8var;

void O8ind(GRID* g)
{
    FOREACH cell IN grid|height{1..(g->height-1)}
    {
        GVAL v0 = REDUCE(+,N={0..2},gv_o8param[N][cell] * gv_grad[cell.edge(N)]);
        GVAL v1 = REDUCE(+,N={0..2},gv_o8param[N][cell] * gv_grad[cell.edge(N).below()]);
        gv_o8var[cell] = gv_o8par2[cell] * v0 + (1-gv_o8par2[cell]) * v1;
    }
    
    FOREACH cell IN grid|height{(g->height-1)..(g->height-1)}
    {
        GVAL v0 = REDUCE(+,N={0..2},gv_o8param[N][cell] * gv_grad[cell.edge(N)]);
        GVAL v1 = REDUCE(+,N={0..2},gv_o8param[N][cell] * gv_grad[cell.edge(N).below()]);
        GVAL v2 = REDUCE(+,N={0..2},gv_o8param[N][cell] * gv_grad[cell.edge(N).below(2)]);
        gv_o8var[cell] = 0.4 * v0 + 0.3 * v1 + 0.3 * v2;
    }
}
