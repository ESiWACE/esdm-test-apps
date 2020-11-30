#!/bin/bash

git clone https://github.com/TUM-I5/SWE.git
cd SWE
git submodule update --init --recursive
cd ..
# Must remove EARLY MPI Finalize and add global size
# sed -i "s#MPI_Finalize#//MPI_Finalize#" SWE/src/examples/swe_mpi.cpp
cp swe_mpi.cpp SWE/src/examples/swe_mpi.cpp
rm SWE/src/writer/Writer.hh
