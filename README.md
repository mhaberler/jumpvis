# jumpvis

visualizes parachute jumps by converting .txt and .gpx to czml for Cesium.js

# Installation on Windows

install Python3 from https://www.python.org/downloads/windows/

install git bash from https://gitforwindows.org/

run git bash

commands:

git clone https://github.com/mhaberler/jumpvis

cd jumpvis

pip3 install gpxpy czml3

now run:

python3 jumpvis.py Beispiel_1.txt Beispiel_1.gpx > Beispiel_1.czml

Open https://cesium.com/cesiumjs/cesium-viewer/ in Chrome
drag and drop Beispiel_1.czml onto the browser window
