#!/bin/bash

source ../source.sh

CFLAGS="-mtune=native -fstrict-aliasing -fargument-noalias -fopenmp -DNDEBUG -DWAVE_PROPAGATION_SOLVER=1 -DPRINT_NETCDFWRITER_INFORMATION -DSOLVER_FWAVE -DWRITENETCDF -DCOUNTFLOPS -DUSEMPI -Ibuild/ -ISWE/src -ISWE/src/include $CFLAGS -fmessage-length=0 -O3"
CXX=mpiCC

mkdir -p build/build_SWE_gnu_release_mpi_fwave

$CXX -o build/SWE_WaveAccumulationBlock.o -c $CFLAGS SWE/src/blocks/SWE_WaveAccumulationBlock.cpp
$CXX -o build/SWE_Block.o -c $CFLAGS SWE/src/blocks/SWE_Block.cpp
$CXX -o build/Logger.o -c $CFLAGS SWE/src/tools/Logger.cpp
$CXX -o NetCdfWriter.o -c $CFLAGS SWE/src/writer/NetCdfWriter.cpp
$CXX -o build/Writer.o -c $CFLAGS SWE/src/writer/Writer.cpp
$CXX -o build/swe_mpi.o -c $CFLAGS SWE/src/examples/swe_mpi.cpp

# To test with NetCDF, use:
$CXX -o build/SWE_gnu_release_mpi_fwave.nc build/*.o NetCdfWriter.o $LDFLAGS -lnetcdf

# Test using ESDM:
$CXX -o ESDMWriter.o -c $CFLAGS -ISWE/src/writer/ ESDMWriter.cpp
$CXX -o build/SWE_gnu_release_mpi_fwave.esdm build/*.o ESDMWriter.o $LDFLAGS -lesdmmpi -lesdm -lesdmutils -lsmd

#  mpiexec -np 2 ./build/SWE_gnu_release_mpi_fwave -x 1024 -y 1024 -o "esdm://test" -c 2
