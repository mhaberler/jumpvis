#!/usr/bin/env python3

import csv
import gpxpy
from gpxpy.geo import get_course, distance, Location, LocationDelta
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

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
import argparse
import sys
from itertools import count

para = "https://static.mah.priv.at/cors/paraglider.glb"
plane = "https://static.mah.priv.at/cors/Cesium_Air.glb"
debug = False
mile = 1.852  # km
delta_h = 112  # unerklärlicher, aber notwendiger fudge-Faktor

_serial = count(0)


def dprint(*args, **kwargs):
    if debug:
        print(*args, file=sys.stderr, **kwargs)


def genczml(starttime, lines, gpx, vorlauf=720, nachlauf=720):
    lb = Label(text="Fallschirmspringer",
               show=True,
               scale=0.5,
               pixelOffset={'cartesian2': [50, -30]})

    plist = []
    last = lines[-1]
    secs = float(last['Zeit(s)'])
    dprint("sprungdauer: ", secs)

    first = lines[0]
    groundspeed = float(first['Groundspeed (kt)']) * mile
    hoehe = float(first['Hoehe(m)'])

    dprint("groundspeed km/h:", groundspeed)
    dprint("hoehe m:", hoehe)

    for p in lines:
        sec = float(p['Zeit(s)'])
        alt = float(p['Hoehe(m)'])
        lat = float(p['Breite'].replace(',', '.'))
        lon = float(p['Laenge'].replace(',', '.'))
        plist.extend([sec, lon, lat, alt])

    sprungdauer = timedelta(seconds=secs)

    vorlauf_zeit = starttime  # - timedelta(seconds=vorlauf)
    nachlauf_zeit = starttime + sprungdauer  # timedelta(seconds=nachlauf)

    jump_traj = Position(
        # interpolationDegree=3,
        # interpolationAlgorithm="LAGRANGE",
        epoch=starttime,
        cartographicDegrees=plist)

    red = Color.from_list([255, 0, 0, 255]),
    grn = Color.from_list([0, 255, 0, 255]),
    pathmat = PolylineOutlineMaterial(color=red,
                                      outlineColor=grn,
                                      outlineWidth=4)
    jump_path = Path(material=Material(polylineOutline=pathmat),
                     width=6,
                     leadTime=0,
                     trailTime=100000,
                     resolution=5)

    packets = []
    gpx_packets = []

    if gpx:
        if nachlauf < secs:
            nachlauf = secs + 120
        rot = Color(rgba=(252, 99, 84, 255))
        blau = Color(rgba=(88, 89, 255, 255))
        gruen = Color(rgba=(0, 225, 61, 255))
        gelb = Color(rgba=(251, 227, 89, 255))
        lila = Color(rgba=(229, 80, 229, 255))
        schwarz = Color(rgba=(0, 0, 0, 255))
        weiss = Color(rgba=(255, 255, 255, 255))

        wpcolors = {
            'x-3 min': lila,
            'x-1 min': lila,
            'x-15 sec': lila,
            'HARP': gruen,  # T0
            'Absetzpunkt': blau,
            'Ende Absetzen': rot,
            'Landeplatz': gelb
        }
        sequence = ['x-3min', 'x-1min', 'x-15',
                    'HARP', 'Absetzpunkt', 'Ende Absetzen']
        # waypoints einfärbeln
        wps = dict()
        for w in gpx.waypoints:
            wps[w.name] = w
            href = HeightReferences.NONE
            h = hoehe
            if w.name == 'Landeplatz':
                href = HeightReferences.RELATIVE_TO_GROUND
                h = 50
            p1 = Packet(id=w.name,  # "point%d" % next(_serial),
                        point=Point(color=wpcolors[w.name],
                                    outlineColor=schwarz,
                                    outlineWidth=2,
                                    pixelSize=10,
                                    heightReference=href),
                        position=Position(cartographicDegrees=[
                            w.longitude, w.latitude, h]),
                        )
            gpx_packets.append(p1)

        # Zeiten zuweisen. IHR MURKSER!

        p0 = wps['x-3 min']
        p1 = wps['Absetzpunkt']

        kurs = get_course(p0.latitude, p0.longitude, p1.latitude, p1.longitude)
        dist = distance(p0.latitude, p0.longitude, None,
                        p1.latitude, p1.longitude, None)
        dprint("Kurs: ", kurs)
        gegenkurs = (kurs + 180.0) % 360.0
        dprint("Gegenkurs: ", gegenkurs)
        dprint("Distanz: ", dist)
        m_s = dist / 180.0
        km_h = m_s * 3.6
        dprint("vel km/h: ", km_h)

        vorlauf_distanz = m_s * vorlauf
        nachlauf_distanz = m_s * nachlauf

        vorlauf_locdelta = LocationDelta(
            distance=vorlauf_distanz, angle=gegenkurs)
        nachlauf_locdelta = LocationDelta(
            distance=nachlauf_distanz, angle=kurs)

        t0 = wps['Absetzpunkt']
        t0_loc = Location(latitude=t0.latitude, longitude=t0.longitude)

        vorlauf_loc = t0_loc + vorlauf_locdelta
        nachlauf_loc = t0 + nachlauf_locdelta
        vorlauf_zeit = starttime - timedelta(seconds=vorlauf)
        nachlauf_zeit = starttime + timedelta(seconds=nachlauf)
        dprint("vor+nachlauf: ", vorlauf_loc, nachlauf_loc)

        flight_traj = [
            0,
            vorlauf_loc.longitude,
            vorlauf_loc.latitude,
            hoehe + delta_h,
            vorlauf + nachlauf,
            nachlauf_loc.longitude,
            nachlauf_loc.latitude,
            hoehe + delta_h
        ]
        flight_position = Position(epoch=vorlauf_zeit,
                                   cartographicDegrees=flight_traj)
        flight_po = PolylineOutlineMaterial(color=gelb,
                                            outlineColor=blau,
                                            outlineWidth=4)
        flight_path = Path(material=Material(polylineOutline=flight_po),
                           width=6,
                           leadTime=0,
                           trailTime=100000,
                           resolution=5)
        flight_vehicle = Model(gltf=plane,
                               scale=4.0,
                               heightReference=HeightReferences.NONE,
                               minimumPixelSize=64)

        flight_orientation = Orientation(velocityReference="#position")

        p2 = Packet(id="track%d" % next(_serial),
                    description="der flug",
                    name="flugfpfad",
                    position=flight_position,
                    orientation=flight_orientation,
                    path=flight_path,
                    model=flight_vehicle,
                    viewFrom=ViewFrom(cartesian=Cartesian3Value(values=[-1000, 0, 300])),
                    availability=TimeInterval(start=vorlauf_zeit,
                                              end=nachlauf_zeit))
        gpx_packets.append(p2)

        # ground Path
        # das schaut sehr konfus aus!
        route = gpx.routes[0]
        posn = []
        for rp in route.points:
            dprint(rp)
            posn.extend([rp.longitude, rp.latitude, 100.0])

        sc = SolidColorMaterial(color=gelb)
        m1 = PolylineMaterial(solidColor=sc)
        p1 = PositionList(cartographicDegrees=posn)
        pl = Polyline(width=5,
                      show=True,
                      clampToGround=True,
                      material=m1,
                      positions=p1)
        p3 = Packet(id="route%d" % next(_serial),
                    name=route.name,
                    description=route.description,
                    polyline=pl)

        gpx_packets.append(p3)

    # end if gpx

    clock = IntervalValue(start=vorlauf_zeit,
                          end=nachlauf_zeit,
                          value=Clock(currentTime=vorlauf_zeit, multiplier=10))
    preamble = Preamble(name="Simulierter Fallschirmabsprung",
                        clock=clock)
    packets.append(preamble)
    packets.extend(gpx_packets)

    jump_vehicle = Model(gltf=para,
                         scale=1.0,
                         heightReference=HeightReferences.NONE,
                         minimumPixelSize=64)
    flight_viewfrom = ViewFrom(cartesian=Cartesian3Value(values=[0, -200, 100]))
    flight = Packet(id="track%d" % next(_serial),
                    description="der Sprung",
                    name="Karli",
                    position=jump_traj,
                    label=lb,
                    path=jump_path,
                    model=jump_vehicle,
                    viewFrom=flight_viewfrom,
                    availability=TimeInterval(
                       start=starttime,
                       end=starttime + sprungdauer))
    packets.append(flight)
    simple = Document(packets)
    print(simple.dumps(indent=4))


def main():
    parser = argparse.ArgumentParser(usage='%(prog)s  [-d] [file ...]',
                                     description='generate czml3 from a Heidi txt file' +
                                     'optionally a gpx file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show detailed logging')
    args, files = parser.parse_known_args()
    global debug
    debug = args.debug

    with open(files[0], 'r') as csv_file:
        lines = []
        reader = csv.DictReader(csv_file, delimiter='\t')
        for row in reader:
            lines.append(row)

    gpx = None
    if len(files) > 1:
        with open(files[1], 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

    absprungzeitpunkt = datetime(2020, 7, 12, hour=8)
    genczml(absprungzeitpunkt, lines, gpx, vorlauf=190, nachlauf=720)


if __name__ == "__main__":
    main()
