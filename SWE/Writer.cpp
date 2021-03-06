#include "writer/Writer.hh"
#ifdef WRITEESDM
#include "ESDMWriter.hh"
#elif WRITENETCDF
#include "NetCdfWriter.hh"
#else
#include "VtkWriter.hh"
#endif
#include <memory>

static int fullX, fullY, offsetX, offsetY;
static float originFullX, originFullY;

void setDomain(int x, int y, int offx, int offy, float originx, float originy){
  fullX = x;
  fullY = y;
  offsetX = offx;
  offsetY = offy;
  originFullX = originx;
  originFullY = originy;
}

std::shared_ptr<io::Writer> io::Writer::createWriterInstance(std::string &fileName, const Float2D &bathymetry,
                                          const BoundarySize &boundarySize, int nX, int nY,
                                          float dX, float dY, float offsetX, float offsetY,
                                          float originX, float originY, int flush) {
    #ifdef WRITEESDM
        auto writer = std::make_shared<io::ESDMWriter>( fileName,
                bathymetry,
                boundarySize,
                nX, nY,
                dX, dY,
                originX, originY,
                flush, fullX, fullY, offsetX, offsetY, originFullX, originFullY);
    #elif WRITENETCDF
    //construct a NetCdfWriter
    auto writer = std::make_shared<io::NetCdfWriter>( fileName,
            bathymetry,
            boundarySize,
            nX, nY,
            dX, dY,
            originX, originY,
            flush);
    #else
    // Construct a VtkWriter
    auto writer = std::make_shared<io::VtkWriter>(fileName,
            bathymetry,
            boundarySize,
            nX, nY,
            dX, dY,
            offsetX, offsetY);
    #endif
    return writer;
}
