import logging
import sys

import xarray as xr  # http://xarray.pydata.org/
from metpy.units import units
import metpy.calc as mpcalc

from czml3 import Packet
from czml3.properties import (
    # Billboard,
    # Clock,
    Color,
    # Label,
    # Point,
    # Material,
    # Model,
    # ViewFrom,
    # Orientation,
    # Path,
    # Position,
    PositionList,
    Polyline,
    SolidColorMaterial,
    # PolylineOutlineMaterial,
    PolylineArrowMaterial,
    # PolylineDashMaterial,
    # PolylineMaterial
)

import seaborn as sns

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
                 bbox=None,
                 windcolors="viridis"):
        self.wind_colormap = sns.color_palette(windcolors, as_cmap=True)
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
        logging.debug("%s: data_vars %s", netcdf, ds.data_vars)
        logging.debug("valid_time %s", ds.valid_time)
        logging.debug("time %s", ds.time)
        logging.debug("step %s", ds.step)

    def czml_wind_vectors(self, layer):

        wind_packets = []
        speed_scale = 100
        for lat in self.ds.coords['latitude']:
            for lon in self.ds.coords['longitude']:
                u = self.ds.u.sel(latitude=lat, longitude=lon,
                                  generalVerticalLayer=layer)
                v = self.ds.v.sel(latitude=lat, longitude=lon,
                                  generalVerticalLayer=layer)
                w = self.ds.wz.sel(latitude=lat, longitude=lon,
                                   generalVerticalLayer=layer)
                t = self.ds.t.sel(latitude=lat, longitude=lon,
                                  generalVerticalLayer=layer)
                qv = self.ds.q.sel(latitude=lat, longitude=lon,
                                  generalVerticalLayer=layer)

                p = self.ds.pres.sel(latitude=lat, longitude=lon,
                                  generalVerticalLayer=layer)

                tempK = float(t) * units.K
                celsius = tempK.to('degC').magnitude

                # Dewpoint K
                dewpt = mpcalc.dewpoint_from_specific_humidity(qv, t, p)

                # relative humidity
                relhum = mpcalc.relative_humidity_from_dewpoint(t, dewpt)

                height = self.ds.h.sel(
                    latitude=lat, longitude=lon, generalVerticalLayer=layer)
                ms = mpcalc.wind_speed(u, v) * units.kt
                wdir = mpcalc.wind_direction(u, v, convention='from')

                logging.debug("%f %f %f %3.1f %3.1f", float(lat), float(
                    lon), float(height), ms.magnitude, wdir.magnitude)

                logging.debug("wind direction %f", wdir.magnitude)  # radians
                logging.debug("wind speed %f", ms.magnitude)

                latend, lonend = getEndpoint(lat, lon, wdir.
                                             magnitude,
                                             ms.magnitude * speed_scale)
                plist = PositionList(cartographicDegrees=[float(lon),
                                                          float(lat),
                                                          float(height),
                                                          lonend, latend, float(height)])

                if True:
                    # norm = matplotlib.colors.Normalize(vmin=10.0, vmax=20.0)
                    # print(norm(15.0)) # 0.5

                    ratio = float(height)/6000.
                    arrow_color = SolidColorMaterial(color=Color(rgbaf=self.wind_colormap(ratio)))
                else:
                    arrow_rgba = [200, 200, 0, 255]
                    arrow_color = SolidColorMaterial(color=Color(rgba=arrow_rgba))

                mat = PolylineArrowMaterial(polylineArrow=arrow_color)
                pl = Polyline(width=5,
                              #show=True,
                              #clampToGround=False,
                              material=mat,
                              positions=plist)
                p3 = Packet(id="%4.fm wind %3.1fkt %3.0f' %3.1f°/%3.1f° rh %2.0f%%" % (
                    height,
                    ms.magnitude,
                    wdir.magnitude,
                    celsius, dewpt.to('degC').magnitude,relhum*100),
                    polyline=pl)

                wind_packets.append(p3)

        return wind_packets
