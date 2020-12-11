#!/bin/bash

source ../source.sh

CFLAGS="-mtune=native -fstrict-aliasing -fargument-noalias -fopenmp -DNDEBUG -DWAVE_PROPAGATION_SOLVER=1 -DPRINT_NETCDFWRITER_INFORMATION -DSOLVER_FWAVE -DWRITENETCDF -DCOUNTFLOPS -DUSEMPI -I. -Ibuild/ -ISWE/src -ISWE/src/include $CFLAGS -fmessage-length=0 -O0 -g3"
CXX=mpiCC

mkdir -p build/build_SWE_gnu_release_mpi_fwave

$CXX -o build/SWE_WaveAccumulationBlock.o -c $CFLAGS SWE/src/blocks/SWE_WaveAccumulationBlock.cpp
$CXX -o build/SWE_Block.o -c $CFLAGS SWE/src/blocks/SWE_Block.cpp
$CXX -o build/Logger.o -c $CFLAGS SWE/src/tools/Logger.cpp
$CXX -o build/swe_mpi.o -c $CFLAGS SWE/src/examples/swe_mpi.cpp

$CXX -o NetCdfWriter.o -c $CFLAGS SWE/src/writer/NetCdfWriter.cpp
$CXX -o Writer.o -c  -ISWE/src/  -ISWE/src/writer/ $CFLAGS Writer.cpp

# To test with NetCDF, use:
$CXX -o build/SWE_gnu_release_mpi_fwave.nc build/*.o Writer.o NetCdfWriter.o $LDFLAGS -lnetcdf

# Test using ESDM:
$CXX -o ESDMWriter.o -c $CFLAGS -I. -ISWE/src/writer/ ESDMWriter.cpp
$CXX -o Writer-ESDM.o -c $CFLAGS -DWRITEESDM -I. -ISWE/src/writer/ Writer.cpp
$CXX -o build/SWE_gnu_release_mpi_fwave.esdm build/*.o Writer-ESDM.o ESDMWriter.o $LDFLAGS -lesdmmpi -lesdm -lsmd

#  mpiexec -np 2 ./build/SWE_gnu_release_mpi_fwave -x 1024 -y 1024 -o "esdm://test" -c 2
