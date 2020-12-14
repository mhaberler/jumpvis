import logging
import xarray as xr  # http://xarray.pydata.org/
import netCDF4 as nc
from metpy.units import units
import metpy.calc as mpcalc

from czml3 import Document, Packet, Preamble

from czml3.properties import (
    Billboard,
    Clock,
    Color,
    Label,
    Point,
    Material,
    Model,
    ViewFrom,
    Orientation,
    Path,
    Position,
    PositionList,
    Polyline,
    SolidColorMaterial,
    PolylineOutlineMaterial,
    PolylineArrowMaterial,
    PolylineDashMaterial,
    PolylineMaterial
)
from czml3.types import (
    IntervalValue,
    Sequence,
    TimeInterval,
    format_datetime_like,
    Cartesian3Value,
    CartographicDegreesListValue,
    CartographicRadiansListValue
)
from czml3.enums import (
    HeightReferences,
    HorizontalOrigins,
    InterpolationAlgorithms,
    LabelStyles,
    ReferenceFrames,
    VerticalOrigins,
)
from geographiclib.constants import Constants
from geographiclib.geodesic import Geodesic

# https://stackoverflow.com/questions/33001420/find-destination-coordinates-given-starting-coordinates-bearing-and-distance
# https://stackoverflow.com/a/33026930/2468365

# cartographicdegrees cartographicdegrees  degrees meters
def getEndpoint(lat1, lon1, bearing, distance):
    geod = Geodesic(Constants.WGS84_a, Constants.WGS84_f)
    d = geod.Direct(lat1, lon1, bearing, distance)
    return d['lat2'], d['lon2']


class Meteo:

    def __init__(self,
                 netcdf=None,
                 bbox=None):
        self.bbox = bbox
        if self.bbox:
            ds = xr.open_dataset(netcdf)
            self.ds = ds.where((ds.t.latitude > self.bbox['min_latitude']) &
                               (ds.t.latitude < self.bbox['max_latitude']) &
                               (ds.t.longitude > self.bbox['min_longitude']) &
                               (ds.t.longitude < self.bbox['max_longitude']), drop=True)
            ds.close()
        else:
            self.ds = xr.open_dataset(netcdf)
        logging.debug(self)

    def czml_wind_vectors(self):

        wind_packets = []
        speed_scale = 1000
        layer = 55
        for lat in self.ds.coords['latitude']:
            for lon in self.ds.coords['longitude']:
                u = self.ds.u.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                v = self.ds.v.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                w = self.ds.wz.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                height = self.ds.h.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                ms = mpcalc.wind_speed(u, v)
                wdir = mpcalc.wind_direction(u, v, convention='from')

                logging.debug("%f %f %f %3.1f %3.1f", float(lat),float(lon), float(height),ms.magnitude, wdir.magnitude)

                logging.debug("wind direction %f", wdir.magnitude) # radians
                logging.debug("wind speed %f", ms.magnitude)


                #p1 = Position(cartographicDegrees=[float(lon), float(lat), float(height)])
                latend, lonend = getEndpoint(lat, lon, wdir.magnitude, ms.magnitude* speed_scale)

                #p2 = Position(cartographicDegrees=[lonend, latend, float(height)])

                plist = PositionList(cartographicDegrees=[float(lon), float(lat), float(height),
                                                          lonend, latend, float(height)])
                #a = PolylineArrowMaterial(color=Color(rgba=[200, 100, 30, 255]))
                sc = SolidColorMaterial(color=Color(rgba=[200, 100, 30, 255]))
                a = PolylineMaterial(solidColor=sc)
                pl = Polyline(width=5,
                              show=True,
                              clampToGround=False,
                              material=a,
                              positions=plist)
                p3 = Packet(
                    # id="route%d" % next(_serial),
                    #         name=route.name,
                    #         description=route.description,
                            polyline=pl)

                wind_packets.append(p3)

        #logging.debug(wind_packets)
        return wind_packets


        # {
        #     "id": "a4b1c111-5b65-4c71-8b5f-4839028d848e",
        #     "polyline": {
        #         "positions": {
        #             "cartographicDegrees": [
        #                 15.219999999999985,
        #                 47.10000000000017,
        #                 1198.722900390625,
        #                 15.21398075673326,
        #                 47.10704914689421,
        #                 1198.722900390625
        #             ]
        #         },
        #         "show": true,
        #         "width": 5,
        #         "material": {
        #             "solidColor": {
        #                 "color": {
        #                     "rgba": [
        #                         200,
        #                         100,
        #                         30,
        #                         255
        #                     ]
        #                 }
        #             }
        #         },
        #         "clampToGround": false
        #     }
        # }

# var purpleArrow = viewer.entities.add({
#   name: "Purple straight arrow at height",
#   polyline: {
#     positions: Cesium.Cartesian3.fromDegreesArrayHeights([
#       -75,
#       43,
#       500000,
#       -125,
#       43,
#       500000,
#     ]),
#     width: 10,
#     arcType: Cesium.ArcType.NONE,
#     material: new Cesium.PolylineArrowMaterialProperty(
#       Cesium.Color.PURPLE
#     ),
#   },
# });
