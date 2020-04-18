#!/bin/bash

source ../source.sh

CFLAGS="-mtune=native -fstrict-aliasing -fargument-noalias -fopenmp -DNDEBUG -DWAVE_PROPAGATION_SOLVER=1 -DPRINT_NETCDFWRITER_INFORMATION -DSOLVER_FWAVE -DWRITENETCDF -DCOUNTFLOPS -DUSEMPI -Ibuild/ -ISWE/src -ISWE/src/include $CFLAGS -fmessage-length=0 -O3"
CXX=mpiCC

# Test using ESDM:
$CXX -g -o ESDMWriter.o -c $CFLAGS -ISWE/src/writer/ -I. ESDMWriter.cpp
$CXX -g -o build/SWE_gnu_release_mpi_fwave.esdm build/*.o Writer-ESDM.o ESDMWriter.o $LDFLAGS -lesdmmpi -lesdm -lesdmutils -lsmd
