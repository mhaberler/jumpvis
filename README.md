# jumpvis

visualizes parachute jumps by converting .txt and .gpx to czml for Cesium.js

# Installation on Windows

install Python3 from https://www.python.org/downloads/windows/

install git bash from https://gitforwindows.org/

run git bash

commands:

pip3 install gpxpy

git clone https://github.com/poliastro/czml3.git

cd czml3

python setup.py install

cd ..

git clone https://github.com/mhaberler/jumpvis

cd jumpvis



Windows:

python.exe jumpvis.py Beispiel_3.txt Beispiel_3.gpx > Beispiel_3.czml

MacOS, Linux:

python3 jumpvis.py Beispiel_3.txt Beispiel_3.gpx >Beispiel_3.czml

Open https://cesium.com/cesiumjs/cesium-viewer/ in Chrome
drag and drop Beispiel_3.czml onto the browser window
