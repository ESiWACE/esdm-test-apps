#include <string>
#include <vector>
#include <iostream>
#include <cassert>

#include <writer/Writer.hh>

namespace io {
  class ESDMWriter;
}

// include ESDM containers from C++ code via:
#include <esdm.h>
#include <esdm-mpi.h>

class io::ESDMWriter : public io::Writer {
private:
    esdm_container_t * container;
    esdm_dataset_t   * tvar;
    esdm_dataset_t   * hvar;
    esdm_dataset_t   * hvvar;
    esdm_dataset_t   * huvar;
    esdm_dataset_t   * bvar;

    int offsetX;
    int offsetY;

    /** Flush after every x write operation? */
    unsigned int flush;
    int rank;

    // writer time dependent variables.
    void writeVarTimeDependent( const Float2D &i_matrix, esdm_dataset_t * dset);
    // writes time independent variables.
    void writeVarTimeIndependent( const Float2D &i_matrix, esdm_dataset_t * dset);

  public:
    ESDMWriter(const std::string &i_fileName,
    			 const Float2D &i_b,
                 const BoundarySize &i_boundarySize,
                 int i_nX, int i_nY,
                 float i_dX, float i_dY,
                 float i_originX = 0., float i_originY = 0.,
                 unsigned int i_flush = 0,
                 int fullX = 0, int fullY = 0, int offsetX = 0, int offsetY = 0, float originX = 0, float originY = 0);
    virtual ~ESDMWriter();

    // writes the unknowns at a given time step
    void writeTimeStep( const Float2D &i_h, const Float2D &i_hu, const Float2D &i_hv, float i_time);
};
