#!/usr/bin/env python3

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx
import gpxpy.gpxxml as mod_gpxxml
import gpxpy.gpxfield as mod_gpxfield
import gpxpy.parser as mod_parser
import gpxpy.geo as mod_geo

from datetime import datetime, timedelta,timezone

def main():
    start = datetime(2020, 7, 12, 8, tzinfo=timezone.utc)

    gpx = mod_gpx.GPX()
    gpx.version = '1.1'
    gpx.name = "Dateiname"
    gpx.description = "Validiertes GPX-Beispiel ohne Sonderzeichen"
    gpx.author_name = "Heidi Schmid"

    gpx.waypoints.append( mod_gpx.GPXRoutePoint(latitude=47.0293469500447,
                               longitude=15.2251027554732,
                               name='x-1 min',
                               symbol='WP',
                               time=start +  timedelta(seconds=120)))

    gpx.waypoints.append(mod_gpx.GPXRoutePoint(latitude=46.9444518397904,
                               longitude=15.1798069010275,
                               name='x-3 min',
                               symbol='WP',
                               time=start +  timedelta(seconds=0)))


    gpx.waypoints.append(mod_gpx.GPXRoutePoint(latitude=47.0611826163901,
                               longitude=15.1628023691719,
                               name='x-15 sec',
                               symbol='WP',
                               time=start +  timedelta(seconds=120)))

    # etc etc

    
    route = mod_gpx.GPXRoute()
    route.name = "Absetzvorgang"
    route.description = "Verbindet die wichtigen Punkte beim Absetzen"
    gpx.routes.append(route)

    rp1 = mod_gpx.GPXRoutePoint(name="Absetzpunk",
                                latitude=47.0717945051719,
                                longitude=15.1571319351276,
                                time=start +  timedelta(seconds=120))
    gpx.routes[0].points.append(rp1)

    rp2 = mod_gpx.GPXRoutePoint(name="Ende Freifall",
                                latitude=47.0873586087185,
                                longitude=15.1488132558242,
                                time=start +  timedelta(seconds=180))
    gpx.routes[0].points.append(rp2)
    # etc etc

    print(gpx.to_xml())


if __name__ == "__main__":
    main()
