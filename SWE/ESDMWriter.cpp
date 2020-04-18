#include <string>
#include <vector>
#include <iostream>
#include <cassert>

#include <writer/Writer.hh>

namespace io {
  class NetCdfWriter;
}

// include ESDM containers from C++ code via:
#include <esdm.h>
#include <esdm-mpi.h>

class io::NetCdfWriter : public io::Writer {
private:
    esdm_container_t * container;
    esdm_dataset_t   * tvar;
    esdm_dataset_t   * xvar;
    esdm_dataset_t   * yvar;
    esdm_dataset_t   * hvar;
    esdm_dataset_t   * hvvar;
    esdm_dataset_t   * huvar;
    esdm_dataset_t   * bvar;

    /** Flush after every x write operation? */
    unsigned int flush;

    // writer time dependent variables.
    void writeVarTimeDependent( const Float2D &i_matrix, esdm_dataset_t * dset);
    // writes time independent variables.
    void writeVarTimeIndependent( const Float2D &i_matrix, esdm_dataset_t * dset);

  public:
    NetCdfWriter(const std::string &i_fileName,
    			 const Float2D &i_b,
                 const BoundarySize &i_boundarySize,
                 int i_nX, int i_nY,
                 float i_dX, float i_dY,
                 float i_originX = 0., float i_originY = 0.,
                 unsigned int i_flush = 0);
    virtual ~NetCdfWriter();

    // writes the unknowns at a given time step
    void writeTimeStep( const Float2D &i_h, const Float2D &i_hu, const Float2D &i_hv, float i_time);
};

static inline void checkRet(esdm_status ret){
  	if (ret != ESDM_SUCCESS) {
      printf("ERROR: ESDM return value isn't success!\n");
  		assert(false);
  		exit(1);
  	}
}

struct esdm_write_request_t {

};

typedef struct esdm_write_request_t esdm_write_request_t;

esdm_status esdm_write_req_start(esdm_write_request_t * req_out, esdm_dataset_t * dset, esdm_dataspace_t * file_space);
esdm_status esdm_write_req_commit(esdm_write_request_t * req);
#define esdm_write_req_pack_float(req, data)

esdm_status esdm_write_req_start(esdm_write_request_t * req_out, esdm_dataset_t * dset, esdm_dataspace_t * file_space){
  return ESDM_SUCCESS;
}

esdm_status esdm_write_req_commit(esdm_write_request_t * req){
    return ESDM_SUCCESS;
}


/**
 * Create an ESDM container
 * Any existing container will be replaced.
 *
 * @param i_baseName base name of the ESDM-container to which the data will be written to.
 * @param i_nX number of cells in the horizontal direction.
 * @param i_nY number of cells in the vertical direction.
 * @param i_dX cell size in x-direction.
 * @param i_dY cell size in y-direction.
 * @param i_originX
 * @param i_originY
 * @param i_flush If > 0, flush data to disk every i_flush write operation
 * @param i_dynamicBathymetry
 */
io::NetCdfWriter::NetCdfWriter( const std::string &i_baseName,
		const Float2D &i_b,
		const BoundarySize &i_boundarySize,
		int i_nX, int i_nY,
		float i_dX, float i_dY,
		float i_originX, float i_originY,
		unsigned int i_flush) :
    io::Writer(i_baseName, i_b, i_boundarySize, i_nX, i_nY), flush(i_flush)
{
	//create a ESDM-container, an existing container will be replaced
  esdm_status ret = esdm_mpi_container_create(MPI_COMM_WORLD, i_baseName.c_str(), true, & container);
  checkRet(ret);

  smd_attr_t * attr;

	//set attributes to match CF-1.5 convention
  attr = smd_attr_new("Conventions", SMD_DTYPE_STRING, "CF-1.5");
  esdm_container_link_attribute(container, 1, attr);
  attr = smd_attr_new("title", SMD_DTYPE_STRING, "Computed tsunami solution");
  esdm_container_link_attribute(container, 1, attr);
  attr = smd_attr_new("history", SMD_DTYPE_STRING, "SWE");
  esdm_container_link_attribute(container, 1, attr);
	attr = smd_attr_new("institution",  SMD_DTYPE_STRING, "Technische Universitaet Muenchen, Department of Informatics, Chair of Scientific Computing");
  esdm_container_link_attribute(container, 1, attr);
	attr = smd_attr_new("source",  SMD_DTYPE_STRING, "Bathymetry and displacement data.");
  esdm_container_link_attribute(container, 1, attr);
	attr = smd_attr_new("references",  SMD_DTYPE_STRING, "http://www5.in.tum.de/SWE");
  esdm_container_link_attribute(container, 1, attr);
	attr = smd_attr_new("comment",  SMD_DTYPE_STRING, "SWE is free software and licensed under the GNU General Public License. Remark: In general this does not hold for the used input data.");
  esdm_container_link_attribute(container, 1, attr);

	//variables add rest of CF-1.5
  esdm_dataspace_t *dspace;
  int64_t b1[] = {0};
  ret = esdm_dataspace_create(1, b1, SMD_DTYPE_FLOAT, & dspace);
  checkRet(ret);
  ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "time", dspace, & tvar);
	checkRet(ret);
  attr = smd_attr_new("long_name", SMD_DTYPE_STRING, "Time");
  esdm_dataset_link_attribute(tvar, 1, attr);
  attr = smd_attr_new("units", SMD_DTYPE_STRING, "seconds since simulation start");
  esdm_dataset_link_attribute(tvar, 1, attr);

  {
    int64_t b[] = {nX};
    ret = esdm_dataspace_create(1, b, SMD_DTYPE_FLOAT, & dspace);
    checkRet(ret);
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "x", dspace, & xvar);
  	checkRet(ret);
  }
  {
    int64_t b[] = {nY};
    ret = esdm_dataspace_create(1, b, SMD_DTYPE_FLOAT, & dspace);
    checkRet(ret);
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "y", dspace, & yvar);
  	checkRet(ret);
  }
  {
    int64_t b[] = {0, nY, nX};
    ret = esdm_dataspace_create(3, b, SMD_DTYPE_FLOAT, & dspace);
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "h", dspace, & hvar);
  	checkRet(ret);
    ret = esdm_dataspace_create(3, b, SMD_DTYPE_FLOAT, & dspace); // TODO: was this needed?
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "hu", dspace, & huvar);
  	checkRet(ret);
    ret = esdm_dataspace_create(3, b, SMD_DTYPE_FLOAT, & dspace);
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "hv", dspace, & hvvar);
  	checkRet(ret);
  }
  {
    int64_t b[] = {nY, nX};
    ret = esdm_dataspace_create(2, b, SMD_DTYPE_FLOAT, & dspace);
    ret = esdm_mpi_dataset_create(MPI_COMM_WORLD, container, "b", dspace, & bvar);
    checkRet(ret);
  }

  //setup grid size
  {
    esdm_write_request_t ew;
    int64_t b[] = {nX};
    ret = esdm_dataspace_create(1, b, SMD_DTYPE_FLOAT, & dspace);
    ret = esdm_write_req_start(& ew, xvar, dspace);
    checkRet(ret);

  	for(size_t i = 0; i < nX; i++) {
      float gridPosition = i_originX + (float).5 * i_dX * (i + 1);
      esdm_write_req_pack_float(& ew, & gridPosition);
  	}
    esdm_write_req_commit(& ew);
  }

  {
    esdm_write_request_t ew;
    int64_t b[] = {nY};
    ret = esdm_dataspace_create(1, b, SMD_DTYPE_FLOAT, & dspace);
    ret = esdm_write_req_start(& ew, yvar, dspace);
    checkRet(ret);

  	for(size_t i = 0; i < nY; i++) {
      float gridPosition = i_originY + (float).5 * i_dY * (i + 1);
      esdm_write_req_pack_float(& ew, & gridPosition);
  	}
    esdm_write_req_commit(& ew);
  }
}

/**
 * Destructor
 */
io::NetCdfWriter::~NetCdfWriter() {
	esdm_container_close(container);
}

/**
 * Writes time dependent data to a ESDM-container (-> constructor) with respect to the boundary sizes.
 *
 * boundarySize[0] == left
 * boundarySize[1] == right
 * boundarySize[2] == bottom
 * boundarySize[3] == top
 *
 * @param i_matrix array which contains time dependent data.
 * @param i_boundarySize size of the boundaries.
 * @param i_ncVariable time dependent ESDM-variable to which the output is written to.
 */
void io::NetCdfWriter::writeVarTimeDependent( const Float2D &i_matrix, esdm_dataset_t * dset) {
	//write col wise, necessary to get rid of the boundary
	//storage in Float2D is col wise
	//read carefully, the dimensions are confusing
	size_t start[] = {timeStep, 0, 0};
	size_t count[] = {1, nY, 1};

  esdm_dataspace_t *dspace;
  esdm_status ret;
  //esdm_dataspace_create(3, b, SMD_DTYPE_FLOAT, & dspace);

  esdm_write_request_t ew;
  ret = esdm_write_req_start(& ew, xvar, dspace);
  checkRet(ret);

	for(unsigned int col = 0; col < nX; col++) {
		start[2] = col; //select col (dim "x")
		// TODO nc_put_vara_float(dataFile, i_ncVariable, start, count,	&i_matrix[col+boundarySize[0]][boundarySize[2]]); //write col
  }
  ret = esdm_write_req_commit(& ew);
}

/**
 * Write time independent data to a ESDM-container (-> constructor) with respect to the boundary sizes.
 * Variable is time-independent
 * boundarySize[0] == left
 * boundarySize[1] == right
 * boundarySize[2] == bottom
 * boundarySize[3] == top
 *
 * @param i_matrix array which contains time independent data.
 * @param i_boundarySize size of the boundaries.
 * @param i_ncVariable time independent ESDM-variable to which the output is written to.
 */
void io::NetCdfWriter::writeVarTimeIndependent( const Float2D &i_matrix, esdm_dataset_t * dset ) {
	//write col wise, necessary to get rid of the boundary
	//storage in Float2D is col wise
	//read carefully, the dimensions are confusing
	size_t start[] = {0, 0};
	size_t count[] = {nY, 1};
	for(unsigned int col = 0; col < nX; col++) {
		start[1] = col; //select col (dim "x")
		// TODO nc_put_vara_float(dataFile, i_ncVariable, start, count,	&i_matrix[col+boundarySize[0]][boundarySize[2]]); //write col
  }
}

/**
 * Writes the unknwons to a ESDM-container (-> constructor) with respect to the boundary sizes.
 *
 * boundarySize[0] == left
 * boundarySize[1] == right
 * boundarySize[2] == bottom
 * boundarySize[3] == top
 *
 * @param i_h water heights at a given time step.
 * @param i_hu momentums in x-direction at a given time step.
 * @param i_hv momentums in y-direction at a given time step.
 * @param i_boundarySize size of the boundaries.
 * @param i_time simulation time of the time step.
 */
void io::NetCdfWriter::writeTimeStep( const Float2D &i_h,
                                      const Float2D &i_hu,
                                      const Float2D &i_hv,
                                      float i_time) {
	if (timeStep == 0){
    // Write bathymetry
    writeVarTimeIndependent(b, bvar);
  }

	//write i_time
	// TODO: nc_put_var1_float(dataFile, timeVar, &timeStep, &i_time);

	//write water height
	writeVarTimeDependent(i_h, hvar);

	//write momentum in x-direction
	writeVarTimeDependent(i_hu, huvar);

	//write momentum in y-direction
	writeVarTimeDependent(i_hv, hvvar);

	// Increment timeStep for next call
	timeStep++;

	if (flush > 0 && timeStep % flush == 0){
    esdm_status ret = esdm_mpi_container_commit(MPI_COMM_WORLD, container);
  }
}