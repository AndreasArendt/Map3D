import sys
import os

utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../submodules/utils/python'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from transformation import wgs84_to_ecef, ecef_to_wgs84

from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import Overpass
import requests
import math

nominatim = Nominatim()

osm_file_path = 'data/map.osm'

def query_tile(address, radius):
    #https://overpass-api.de/api/map?bbox=11.47825,48.14859,11.48350,48.15251
    min_lat, min_lon, max_lat, max_lon = get_bounding_box(address, radius)   

    # Format the URL for the Overpass API request
    url = f"https://overpass-api.de/api/map?bbox={min_lon},{max_lat},{max_lon},{min_lat}"

    # Send the GET request
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the OSM data to a file
        with open(osm_file_path, "wb") as file:
            file.write(response.content)
        print("OpenStreetMap data downloaded successfully.")
    else:
        print("Error downloading OpenStreetMap data:", response.status_code, response.reason)

    return osm_file_path


def query_tile_overpass(address, radius):
    min_lat, min_lon, max_lat, max_lon = get_bounding_box(address, radius)   

    print("downloading...")

    params = dict(
        data = 
        f"""
            [out:xml][timeout:25];
            (
                way({max_lat},{min_lon},{min_lat},{max_lon});
                node({max_lat},{min_lon},{min_lat},{max_lon});
                relation({max_lat},{min_lon},{min_lat},{max_lon});
            );
            out body({max_lat},{min_lon},{min_lat},{max_lon});  
             (._; >;);        
        """
    )

    print(params['data'])

    resp = requests.get(url=url, params=params)
    # elev = resp.json()

    # Save the result to an OSM file
    with open(osm_file_path, 'w', encoding='utf-8') as file:
        file.write(resp.text)

    print(f"OSM data has been saved to {osm_file_path}")
    return osm_file_path

def get_bounding_box(address, radius):
 # Query the address
    result = nominatim.query(address)

    # Extract and print the coordinates
    if result:
        lat = float(result.toJSON()[0]['lat'])
        lon = float(result.toJSON()[0]['lon'])
    else:
        print("Address not found.")

    url = 'https://api.open-meteo.com/v1/elevation'

    params = dict(
        latitude=lat,
        longitude=lon
    )

    resp = requests.get(url=url, params=params)
    elev = float(resp.json()['elevation'][0])

    print(f"Latitude: {lat}, Longitude: {lon}, Elevation: {elev}")

    # Add utils path
    utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../submodules/utils/python'))
    if utils_path not in sys.path:
        sys.path.append(utils_path)

    # Request Map Tile
    url = 'https://overpass-api.de/api/interpreter'

    x_E, y_E, z_E = wgs84_to_ecef(lat, lon, elev)
    
    max_lat__rad, max_lon__rad, _ = ecef_to_wgs84(x_E + radius/2, y_E + radius/2, z_E)
    min_lat__rad, min_lon__rad, _ = ecef_to_wgs84(x_E - radius/2, y_E - radius/2, z_E)

    max_lat = math.degrees(max_lat__rad)
    min_lat = math.degrees(min_lat__rad)

    max_lon = math.degrees(max_lon__rad)
    min_lon = math.degrees(min_lon__rad)

    print(f"Lat max: {max_lat}, min: {min_lat}, center: {lat}")
    print(f"Lon max: {max_lon}, min: {min_lon}, center: {lon}")

    return min_lat, min_lon, max_lat, max_lon