import logging
import xarray as xr  # http://xarray.pydata.org/
import netCDF4 as nc
from metpy.units import units
import metpy.calc as mpcalc

class Meteo:

    def __init__(self,
                 netcdf=None,
                 bbox=None):

        # format:{'min_latitude': min_lat,
        #         'max_latitude': max_lat,
        #         'min_longitude': min_lon,
        #         'max_longitude': max_lon,
        #         'min_elevation': min_ele,
        #         'max_elevation': max_ele}
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

        layer = 65
        for lat in self.ds.coords['latitude']:
            for lon in self.ds.coords['longitude']:
                u = self.ds.u.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                v = self.ds.v.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                w = self.ds.wz.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                height = self.ds.h.sel(latitude=lat, longitude=lon,generalVerticalLayer=layer)
                ms = mpcalc.wind_speed(u, v)
                wdir = mpcalc.wind_direction(u, v, convention='from')
                wdim = float(w) * units('m/s')
                logging.debug("%f %f %f %s %s %s", float(lat),float(lon), float(height),ms, wdir, wdim)
