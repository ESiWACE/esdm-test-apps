#include "grid.h"
#include "memory.h"

int transform(int n, int x, int y)
{
    int rx, ry, s, d=0, t;
    for (s=n/2; s>0; s/=2) {
        rx = (x & s) > 0;
        ry = (y & s) > 0;
        d += s * s * ((3 * rx) ^ ry);

        if (ry == 0) {
            if (rx) {
                x = n-1 - x;
                y = n-1 - y;
            }

            t  = x;
            x = y;
            y = t;
        }
    }
    return d;
}

void create_maps(GRID *g)
{
    int x=g->height,y=g->height;
    g->map1 = malloc(x*sizeof(int*));
    g->map2 = malloc(g->cellCount*sizeof(map_t));
    for(int i=0; i<x;i++){
        g->map1[i]= malloc(y*sizeof(int));
        for(int j=0; j<y;j++){
            int t = transform(x,i,j);
            g->map1[i][j] = t;
            g->map2[t].i=i;
            g->map2[t].j=j;
        }
    }
}

#ifndef NBRS
#error "please define NBRS"
#endif

#if NBRS==3

int
calc_edge_count (GRID * g)
{
  return (g->cellCount * 3)/2;
}

void
tessellation (GRID * g)
{
  for (int i = 0; i < NBRS; i++)
    {
      g->neighbor[i] = malloc ((g->cellCount) * sizeof (int));
      g->cedge[i] = malloc ((g->cellCount) * sizeof (int));
    }
  for (int i = 0; i < 2; i++)
    {
      g->ecell[i] = malloc ((g->edgeCount) * sizeof (int));
    }
  int x = g->height, y = g->height;
  for (int i = 0; i < x - 1; i++)
    for (int j = 0; j < y; j++)
      g->neighbor[0][g->map1[i][j]] = g->map1[i + 1][j];
  for (int j = 0; j < y; j++)
    g->neighbor[0][g->map1[x - 1][j]] = g->map1[0][j];
  for (int i = 1; i < x; i++)
    for (int j = 0; j < y; j++)
      g->neighbor[1][g->map1[i][j]] = g->map1[i - 1][j];
  for (int j = 0; j < y; j++)
    g->neighbor[1][g->map1[0][j]] = g->map1[x - 1][j];
  for (int i = 0; i < x; i += 2)
    g->neighbor[2][g->map1[i][0]] = g->map1[i][y - 1];
  for (int i = 0; i < x; i += 2)
    for (int j = 2; j < y; j += 2)
      g->neighbor[2][g->map1[i][j]] = g->map1[i][j - 1];
  for (int i = 1; i < x; i += 2)
    for (int j = 1; j < y; j += 2)
      g->neighbor[2][g->map1[i][j]] = g->map1[i][j - 1];
  for (int i = 1; i < x; i += 2)
    for (int j = 0; j < y - 1; j += 2)
      g->neighbor[2][g->map1[i][j]] = g->map1[i][j + 1];
  for (int i = 0; i < x; i += 2)
    for (int j = 1; j < y - 1; j += 2)
      g->neighbor[2][g->map1[i][j]] = g->map1[i][j + 1];
  for (int i = y % 2; i < x; i += 2)
    g->neighbor[2][g->map1[i][y - 1]] = g->map1[i][0];

  for (int c = 0; c < g->cellCount; c++)
    {
      g->cedge[0][c] = (c*3)/2;
      g->cedge[1][g->neighbor[0][c]] = g->cedge[0][c];
      g->ecell[0][g->cedge[0][c]] = g->neighbor[0][c];
      g->ecell[1][g->cedge[0][c]] = c;
    }
  for (int c = 0; c < g->cellCount; c+=2)
    {
      g->cedge[2][c] = (c*3)/2+2;
      g->cedge[2][g->neighbor[2][c]] = g->cedge[2][c];
      g->ecell[0][g->cedge[2][c]] = c;
      g->ecell[1][g->cedge[2][c]] = g->neighbor[2][c];
    }
}

void
init_edge_weights (GRID * g)
{
  GVAL j = -1.0;
  for (int i = 0; i < BLKSIZE; i++)
    {
      g->edge_weights[0][i] = 1.0;
      g->edge_weights[1][i] = -1.0;
      g->edge_weights[2][i] = j;
      j = j * -1;
    }
}

#elif NBRS==4

int calc_edge_count(GRID *g)
{
    return (int)(((float)g->cellCount*NBRS/2.0)+ (2.0*g->height) );
}

void tessellation(GRID* g)
{
    for(int i=0;i<NBRS;i++){
        g->neighbor[i] = malloc((g->cellCount)*sizeof(int));
        g->cedge[i] = malloc((g->cellCount)*sizeof(int));
    }
    for(int i=0;i<2;i++){
        g->ecell[i] = malloc((g->edgeCount)*sizeof(int));
    }

    int x=g->height,y=g->height;
    for(int i=0; i<x;i++){//
        for(int j=0; j<y;j++){
            if(i<x-1) g->neighbor[0][g->map1[i][j]]=g->map1[i+1][j];
            else      g->neighbor[0][g->map1[i][j]]=g->cellCount;
            if(j<y-1) g->neighbor[1][g->map1[i][j]]=g->map1[i][j+1];
            else      g->neighbor[1][g->map1[i][j]]=g->cellCount;
            if(i>0)   g->neighbor[2][g->map1[i][j]]=g->map1[i-1][j];
            else      g->neighbor[2][g->map1[i][j]]=g->cellCount;
            if(j>0)   g->neighbor[3][g->map1[i][j]]=g->map1[i][j-1];
            else      g->neighbor[3][g->map1[i][j]]=g->cellCount;
            
            g->neighbor[0][g->cellCount]=
            g->neighbor[1][g->cellCount]=
            g->neighbor[2][g->cellCount]=
            g->neighbor[3][g->cellCount]=g->cellCount;//
            
            g->cedge[0][g->map1[i][j]] = g->map1[i][j];
            g->cedge[1][g->map1[i][j]] = g->cellCount + g->map1[i][j];
            if(i>0)   g->cedge[2][g->map1[i][j]] = g->map1[i-1][j];
            else      g->cedge[2][g->map1[i][j]] = g->cellCount*2+j;
            if(j>0)   g->cedge[3][g->map1[i][j]] = g->cellCount + g->map1[i][j-1];
            else      g->cedge[3][g->map1[i][j]] = g->cellCount*2+y+i;
            
            g->ecell[1][g->map1[i][j]] = g->map1[i][j];
            g->ecell[1][g->cellCount + g->map1[i][j]] = g->map1[i][j];
            if(i>0)   g->ecell[0][g->map1[i-1][j]] = g->map1[i][j];
            else      g->ecell[0][g->cellCount*2+j] = g->map1[i][j];
            if(j>0)   g->ecell[0][g->cellCount + g->map1[i][j-1]] = g->map1[i][j];
            else      g->ecell[0][g->cellCount*2+y+i] = g->map1[i][j];
            g->ecell[0][g->map1[x-1][j]] = g->cellCount;//TODO: out of loop
            g->ecell[0][g->cellCount + g->map1[i][y-1]] = g->cellCount;//
            g->ecell[1][g->cellCount*2+j] = g->cellCount;//TODO: out of loop
            g->ecell[1][g->cellCount*2+y+i] = g->cellCount;//
        }
    }
}


void init_edge_weights(GRID* g)
{
    for(int i=0;i<BLKSIZE;i++){
        g->edge_weights[0][i]=1.0;
        g->edge_weights[1][i]=1.0;
        g->edge_weights[2][i]=-1.0;
        g->edge_weights[3][i]=-1.0;
    }
}

#elif NBRS==6

int calc_edge_count(GRID *g)
{
    return (int)(((float)g->cellCount*NBRS/2.0)+ (4.0*g->height) -1 );
}

void tessellation(GRID* g)
{
    for(int i=0;i<NBRS;i++){
        g->neighbor[i] = malloc((g->cellCount)*sizeof(int));
        g->cedge[i] = malloc((g->cellCount)*sizeof(int));
    }
    for(int i=0;i<2;i++){
        g->ecell[i] = malloc((g->edgeCount)*sizeof(int));
    }

    int x=g->height,y=g->height;
    for(int i=0; i<x;i++)
        for(int j=0; j<y;j+=2)
            g->neighbor[0][g->map1[i][j]]=g->map1[i][j+1];
    for(int i=0; i<x-1;i++)
        for(int j=1; j<y-1;j+=2)
            g->neighbor[0][g->map1[i][j]]=g->map1[i+1][j+1];
    for(int j=1; j<y-1;j+=2)
            g->neighbor[0][g->map1[x-1][j]]=g->cellCount;
    for(int i=0; i<x;i++)
            g->neighbor[0][g->map1[i][y-1]]=g->cellCount;

    for(int i=0; i<x-1;i++)
        for(int j=0; j<y;j++)
            g->neighbor[1][g->map1[i][j]]=g->map1[i+1][j];
    for(int j=0; j<y;j++)
        g->neighbor[1][g->map1[x-1][j]]=g->cellCount;

    for(int i=0; i<x;i++)
        g->neighbor[2][g->map1[i][0]]=g->cellCount;
    for(int i=0; i<x;i++)
        for(int j=2; j<y;j+=2)
            g->neighbor[2][g->map1[i][j]]=g->map1[i][j-1];
    for(int i=0; i<x-1;i++)
        for(int j=1; j<y;j+=2)
            g->neighbor[2][g->map1[i][j]]=g->map1[i+1][j-1];
    for(int j=1; j<y;j+=2)
            g->neighbor[2][g->map1[x-1][j]]=g->cellCount;

    for(int i=0; i<x;i++)
        g->neighbor[3][g->map1[i][0]]=g->cellCount;
    for(int i=1; i<x;i++)
        for(int j=2; j<y;j+=2)
            g->neighbor[3][g->map1[i][j]]=g->map1[i-1][j-1];
    for(int j=2; j<y;j+=2)
            g->neighbor[3][g->map1[0][j]]=g->cellCount;
    for(int i=0; i<x;i++)
        for(int j=1; j<y;j+=2)
            g->neighbor[3][g->map1[i][j]]=g->map1[i][j-1];
    
    for(int i=1; i<x;i++)
        for(int j=0; j<y;j++)
            g->neighbor[4][g->map1[i][j]]=g->map1[i-1][j];
    for(int j=0; j<y;j++)
        g->neighbor[4][g->map1[0][j]]=g->cellCount;
    
    for(int i=1; i<x;i++)
        for(int j=0; j<y;j+=2)
            g->neighbor[5][g->map1[i][j]]=g->map1[i-1][j+1];
    for(int j=0; j<y;j+=2)
            g->neighbor[5][g->map1[0][j]]=g->cellCount;
    for(int i=0; i<x;i++)
        for(int j=1; j<y-1;j+=2)
            g->neighbor[5][g->map1[i][j]]=g->map1[i][j+1];
    for(int i=0; i<x;i++)
            g->neighbor[5][g->map1[i][y-1]]=g->cellCount;
    
    
    for(int i=0; i<x;i++)
        for(int j=0; j<y;j++){
            g->cedge[0][g->map1[i][j]]=g->map1[i][j];
            g->cedge[1][g->map1[i][j]]=g->cellCount + g->map1[i][j];
            g->cedge[2][g->map1[i][j]]=g->cellCount * 2 + g->map1[i][j];
        }
    for(int i=0; i<x;i++)
        for(int j=0; j<y;j++){
            if(j==0 || ((i==0)&&(j%2==0)))
                g->cedge[3][g->map1[i][j]]= g->cellCount * 3 + (j==0?i:x+j/2-1);
            else
                g->cedge[3][g->map1[i][j]]= g->cedge[0][g->neighbor[3][g->map1[i][j]]];

            if(i==0)
                g->cedge[4][g->map1[i][j]]= g->cellCount * 3 + x+x/2 + j -1;
            else
                g->cedge[4][g->map1[i][j]]= g->cedge[1][g->neighbor[4][g->map1[i][j]]];

            if((j==y-1) || ((i==0)&&(j%2==0)))
                g->cedge[5][g->map1[i][j]]= g->cellCount * 3 + x+x/2 + y -1 + (j==y-1?y/2+i:j/2);
            else
                g->cedge[5][g->map1[i][j]]= g->cedge[2][g->neighbor[5][g->map1[i][j]]];
        }


    for(int c=0; c<g->cellCount ;c++){
        g->ecell[0][g->cedge[0][c]] = g->neighbor[0][c];
        g->ecell[1][g->cedge[0][c]] = c;

        g->ecell[0][g->cedge[1][c]] = g->neighbor[1][c];
        g->ecell[1][g->cedge[1][c]] = c;

        g->ecell[0][g->cedge[2][c]] = g->neighbor[2][c];
        g->ecell[1][g->cedge[2][c]] = c;

        g->ecell[0][g->cedge[3][c]] = c;
        g->ecell[1][g->cedge[3][c]] = g->neighbor[3][c];

        g->ecell[0][g->cedge[4][c]] = c;
        g->ecell[1][g->cedge[4][c]] = g->neighbor[4][c];

        g->ecell[0][g->cedge[5][c]] = c;
        g->ecell[1][g->cedge[5][c]] = g->neighbor[5][c];
    }
}

void init_edge_weights(GRID* g)
{
    for(int i=0;i<BLKSIZE;i++){
        g->edge_weights[0][i]=g->edge_weights[1][i]=g->edge_weights[2][i]=1.0;
        g->edge_weights[3][i]=g->edge_weights[4][i]=g->edge_weights[5][i]=-1.0;
    }
}

#else
#error "supported shapes are traiangles,rectangles and hexagons"
#endif

void init_blocking(GRID*g)
{
    for(int i=0;i<NBRS;i++){
        ALLOC g->cNeighborIdx[i];
        ALLOC g->cNeighborBlk[i];
    }
    int first_cBlock=g->mpi_rank*((g->cBlkCnt+g->mpi_world_size-1)/g->mpi_world_size);
    int first_eBlock=g->mpi_rank*((g->eBlkCnt+g->mpi_world_size-1)/g->mpi_world_size);
    for(int i=0;i<NBRS;i++){
        FOREACH cell IN gridCELL2D
        {
            if((g->mpi_rank==g->mpi_world_size-1) && (cell.block==(g->cBlkCnt-1)%((g->cBlkCnt+g->mpi_world_size-1)/g->mpi_world_size)) && (cell.cell>(g->cellCount-1)%g->blkSize))
            {
              g->cNeighborIdx[i][cell] = cell.cell;
              g->cNeighborBlk[i][cell] = cell.block;
            }
            else
            {
              g->cNeighborIdx[i][cell] = g->neighbor[i][(first_cBlock+cell.block)*g->blkSize+cell.cell]%g->blkSize;
              g->cNeighborBlk[i][cell] = g->neighbor[i][(first_cBlock+cell.block)*g->blkSize+cell.cell]/g->blkSize;
            }
        }
    }
    
    for(int i=0;i<NBRS;i++){
        ALLOC g->cEdgeIdx[i];
        ALLOC g->cEdgeBlk[i];
    }
    for(int i=0;i<NBRS;i++){
        FOREACH cell IN gridCELL2D
        {
            if((g->mpi_rank==g->mpi_world_size-1) && (cell.block==(g->cBlkCnt-1)%((g->cBlkCnt+g->mpi_world_size-1)/g->mpi_world_size)) && (cell.cell>(g->cellCount-1)%g->blkSize))
            {
              g->cEdgeIdx[i][cell] = 0;
              g->cEdgeBlk[i][cell] = first_eBlock;
            }
            else
            {
              g->cEdgeIdx[i][cell] = g->cedge[i][(first_cBlock+cell.block)*g->blkSize+cell.cell]%g->blkSize;
              g->cEdgeBlk[i][cell] = g->cedge[i][(first_cBlock+cell.block)*g->blkSize+cell.cell]/g->blkSize;
            }
        }
    }

    for(int i=0;i<2;i++){
        ALLOC g->eCellIdx[i];
        ALLOC g->eCellBlk[i];
    }
    for(int i=0;i<2;i++){
        FOREACH edge IN gridEDGE2D
        {
            if((g->mpi_rank==g->mpi_world_size-1) && (edge.block==(g->eBlkCnt-1)%((g->eBlkCnt+g->mpi_world_size-1)/g->mpi_world_size)) && (edge.edge>(g->edgeCount-1)%g->blkSize))
            {
              g->eCellIdx[i][edge] = 0;
              g->eCellBlk[i][edge] = first_cBlock;
            }
            else
            {
              g->eCellIdx[i][edge] = g->ecell[i][(first_eBlock+edge.block)*g->blkSize+edge.edge]%g->blkSize;
              g->eCellBlk[i][edge] = g->ecell[i][(first_eBlock+edge.block)*g->blkSize+edge.edge]/g->blkSize;
            }
        }
    }
}

void init_grid(GRID* g, int cellCount, int height){
    g->cellCount = cellCount*cellCount;//cellCount;
    g->height = cellCount;
    g->edgeCount= calc_edge_count(g);
    g->blkSize= BLKSIZE;
    g->cBlkCnt= (g->cellCount+g->blkSize-1)/g->blkSize;
    g->eBlkCnt= (g->edgeCount+g->blkSize-1)/g->blkSize;
    
    create_maps(g);
    tessellation(g);
    g->height = height;
    init_edge_weights(g);
    init_blocking(g);
    INITCOMM;
}

void get_indices_c(GRID* g, int blk, int* cb, int* ce)
{
    *cb = 0;
    *ce = blk==g->cBlkCnt-1 ? g->cellCount%g->blkSize==0 ? g->blkSize : g->cellCount%g->blkSize : g->blkSize;
}

void get_indices_e(GRID* g, int blk, int* eb, int* ee)
{
    *eb = 0;
    *ee = blk==g->eBlkCnt-1 ? g->edgeCount%g->blkSize==0 ? g->blkSize : g->edgeCount%g->blkSize : g->blkSize;
}
