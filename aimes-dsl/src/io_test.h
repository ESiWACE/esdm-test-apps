#include "io.h"

void TestIO(GRID *g)
{
    // TODO: seed the rngfalse
    printf("Init write...\n");
    io_write_init(g, "temp_netcdf_test_output.cdf");

    GVAL CELL 3D test_output1;
    io_var_t io_test_output1;
    GVAL CELL 3D test_input1;
    io_var_t io_test_input1;

    GVAL EDGE 3D test_output2;
    io_var_t io_test_output2;
    GVAL EDGE 3D test_input2;
    io_var_t io_test_input2;

    GVAL CELL 2D test_output3;
    io_var_t io_test_output3;
    GVAL CELL 2D test_input3;
    io_var_t io_test_input3;

    GVAL EDGE 2D test_output4;
    io_var_t io_test_output4;
    GVAL EDGE 2D test_input4;
    io_var_t io_test_input4;
	
    ALLOC test_output1;
    ALLOC test_input1;

    ALLOC test_output2;
    ALLOC test_input2;

    ALLOC test_output3;
    ALLOC test_input3;

    ALLOC test_output4;
    ALLOC test_input4;

    printf("Generate test values...\n");
    FOREACH cell IN grid
    {
	test_output1[cell] = (float)rand();
    }

    FOREACH cell IN gridCELL2D
    {
	test_output3[cell] = (float)rand();
    }

    FOREACH edge IN grid
    {
	test_output2[edge] = (float)rand();
    }

    FOREACH edge IN gridEDGE2D
    {
	test_output4[edge] = (float)rand();
    }

    printf("Setup output variable...\n");
    io_write_define(g,"test_output1", (GVAL *)test_output1, FLOAT32,
		    GRID_POS_CELL, GRID_DIM_3D, &io_test_output1);
    io_write_define(g,"test_output2", (GVAL *)test_output2, FLOAT32,
		    GRID_POS_EDGE, GRID_DIM_3D, &io_test_output2);
    io_write_define(g,"test_output3", (GVAL *)test_output3, FLOAT32,
		    GRID_POS_CELL, GRID_DIM_2D, &io_test_output3);
    io_write_define(g,"test_output4", (GVAL *)test_output4, FLOAT32,
		    GRID_POS_EDGE, GRID_DIM_2D, &io_test_output4);
    io_write_registration_complete(g);

    io_write_announce(g, &io_test_output1);
    io_write_announce(g, &io_test_output2);
    io_write_announce(g, &io_test_output3);
    io_write_announce(g, &io_test_output4);
    printf("Writing to disk...\n");
    io_write_start(g);
		
    io_write_finalize(g);

	
    printf("Init read...\n");
    io_read_init(g, "temp_netcdf_test_output.cdf");

    io_read_register(g, "test_output1", (GVAL *)test_input1, FLOAT32, FLOAT32, GRID_POS_CELL, GRID_DIM_3D);
    io_read_register(g, "test_output2", (GVAL *)test_input2, FLOAT32, FLOAT32, GRID_POS_EDGE, GRID_DIM_3D);
    io_read_register(g, "test_output3", (GVAL *)test_input3, FLOAT32, FLOAT32, GRID_POS_CELL, GRID_DIM_2D);
    io_read_register(g, "test_output4", (GVAL *)test_input4, FLOAT32, FLOAT32, GRID_POS_EDGE, GRID_DIM_2D);
    printf("Reading from disk...\n");
    io_read_start();

    printf("Comparing initial values with disk values...\n");
    int success = 1;
    size_t total = 0;
    size_t count = 0;
    FOREACH cell IN grid
    {
	if(test_output1[cell] != test_input1[cell])
	{
	    count++;
	    success = 0;
	}
    }
    printf("%d/%d errors for CELL 3D\n",count, g->height*g->cellCount);
    total += count;
    count = 0;
    
    FOREACH edge IN grid
    {
	if(test_output2[edge] != test_input2[edge])
	{
	    count++;
	    success = 0;
	}
    }
    printf("%d/%d errors for EDGE 3D\n",count, g->height*g->edgeCount);
    total += count;
    count = 0;
    
    FOREACH cell IN gridCELL2D
    {
	if(test_output3[cell] != test_input3[cell])
	{
	    count++;
	    success = 0;
	}
    }
    printf("%d/%d errors for CELL 2D\n",count, g->cellCount);
    total += count;
    count = 0;
    
    FOREACH edge IN gridEDGE2D
    {
	if(test_output4[edge] != test_input4[edge])
	{
	    count++;
	    success = 0;
	}
    }
    printf("%d/%d errors for EDGE 2D\n",count, g->edgeCount);
    total += count;
    count = 0;

    printf("%d/%d errors total\n",count, g->height*g->cellCount + g->height*g->edgeCount+ g->cellCount+ g->cellCount);
	
    if(success)
    {
	printf("\nnetcdf io test\x1B[32m succeded\x1B[0m\n");
    }
    else
    {
	printf("\nnetcdf io test\x1B[31m failed\x1B[0m\n");
    }
}
