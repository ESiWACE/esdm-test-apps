#include <stdint.h>
#include "../io.h"
#include "../option.h"
#include "../grid.h"

static char *Filename;
static int gridsize = 4;
static int gridheight = 64;

static option_help options [] = {
    {'G', "gridsize", "The dimension of the grid in G*G.H", OPTION_OPTIONAL_ARGUMENT, 'd', & gridsize},
    {'H', "gridheight", "The dimension of the grid in G*G*H.", OPTION_OPTIONAL_ARGUMENT, 'd', & gridheight},
    {'f', "filename", "Path to the output file.", OPTION_REQUIRED_ARGUMENT, 's', &Filename},
    LAST_OPTION
};

void Init_gv_temp(GRID *g)
{
    GVAL CELL 3D gv_temp;
    ALLOC gv_temp;
    io_var_t io_gv_temp;

    FOREACH cell IN grid
    {
	if(cell.block==0 && cell.cell==0 && g->mpi_rank==0)gv_temp[cell]=100.0f;
	else gv_temp[cell]=0.0f;
    }
    io_write_define(g,"gv_temp", (GVAL *)gv_temp, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_3D, &io_gv_temp);
    io_write_announce(g, &io_gv_temp);
}

void Init_gv_ind2Dparam(GRID *g)
{
    GVAL EDGE 2D gv_ind2Dparam;
    ALLOC gv_ind2Dparam;
    io_var_t io_gv_ind2Dparam;

    FOREACH edge IN gridEDGE2D
    {
	gv_ind2Dparam[edge]=1.0f;
    }
    io_write_define(g,"gv_ind2Dparam", (GVAL *)gv_ind2Dparam, FLOAT32, GRID_POS_EDGE,
		    GRID_DIM_2D, &io_gv_ind2Dparam);
    io_write_announce(g, &io_gv_ind2Dparam);
}

void Init_gv_o8param(GRID *g)
{
    GVAL CELL 2D gv_o8param0;
    ALLOC gv_o8param0;
    io_var_t io_gv_o8param0;

    FOREACH cell IN gridCELL2D
    {
	gv_o8param0[cell]=1.0f/3.0f;
    }
    io_write_define(g,"gv_o8param0", (GVAL *)gv_o8param0, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_2D, &io_gv_o8param0);
    io_write_announce(g, &io_gv_o8param0);

    GVAL CELL 2D gv_o8param1;
    ALLOC gv_o8param1;
    io_var_t io_gv_o8param1;

    FOREACH cell IN gridCELL2D
    {
	gv_o8param1[cell]=1.0f/3.0f;
    }
    io_write_define(g,"gv_o8param1", (GVAL *)gv_o8param1, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_2D, &io_gv_o8param1);
    io_write_announce(g, &io_gv_o8param1);

    GVAL CELL 2D gv_o8param2;
    ALLOC gv_o8param2;
    io_var_t io_gv_o8param2;

    FOREACH cell IN gridCELL2D
    {
	gv_o8param2[cell]=1.0f/3.0f;
    }
    io_write_define(g,"gv_o8param2", (GVAL *)gv_o8param2, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_2D, &io_gv_o8param2);
    io_write_announce(g, &io_gv_o8param2);
}

void Init_gv_o8par2(GRID *g)
{
    GVAL CELL 3D gv_o8par2;
    ALLOC gv_o8par2;
	io_var_t io_gv_o8par2;

    FOREACH cell IN grid
    {
	gv_o8par2[cell]=1.0f/2.0f;
    }
    io_write_define(g,"gv_o8par2", (GVAL *)gv_o8par2, FLOAT32, GRID_POS_CELL,
		    GRID_DIM_3D, &io_gv_o8par2);
    io_write_announce(g, &io_gv_o8par2);
}


int main(int argc, char **argv)
{
    int PrintHelp = 0;
    parseOptions(argc ,argv, options, &PrintHelp);
    if(PrintHelp)
    {
	print_help(options, 0);
	exit(0);
    }
    GRID *g = malloc(sizeof(GRID));
    INITCOMMLIB;
    init_grid(g, gridsize, gridheight);
    io_write_init(g, Filename);

    Init_gv_temp(g);
    Init_gv_ind2Dparam(g);
    Init_gv_o8param(g);
    Init_gv_o8par2(g);

    io_write_registration_complete(g);
    io_write_start(g);
    io_write_finalize(g);
    FINCOMMLIB;
}
