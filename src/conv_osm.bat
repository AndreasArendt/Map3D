@echo off

set osm2world=.\submodules\OSM2World
set osm=.\data\map.osm

java --add-exports java.base/java.lang=ALL-UNNAMED --add-exports java.desktop/sun.awt=ALL-UNNAMED --add-exports java.desktop/sun.java2d=ALL-UNNAMED -jar %osm2world%\target\osm2world-0.4.0-SNAPSHOT.jar --config %osm2world%\standard.properties -i %osm% -o data\tile.obj --oview.angle 90