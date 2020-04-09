#include "grid.h"
extern char *restrict levelMask;
extern char *restrict*restrict levMsk;
extern GVAL *restrict vcflMax;
extern GVAL vcflMaxVal;
extern GVAL CELL 3D gv_dvg;

void O10BlkRed(GRID* g)
{
    FOREACH cell IN grid
    {
        if(gv_dvg[cell]>0.0){
            levMsk[cell.block][cell.height] = 1;
            levelMask[cell.height] = 1;
            vcflMax[cell.block] = vcflMax[cell.block]>gv_dvg[cell]?vcflMax[cell.block]:gv_dvg[cell];
        }
    }
    for(int b=0;b<g->cBlkCnt;b++){
        vcflMaxVal = vcflMaxVal>vcflMax[b]?vcflMaxVal:vcflMax[b];
    }
}
