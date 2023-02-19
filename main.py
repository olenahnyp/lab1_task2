"""
Create a map with movies that were shoot the closest to you.
"""
import math
import folium
from geopy.geocoders import Nominatim
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('year', type = int)
parser.add_argument('latitude', type = float)
parser.add_argument('longitude', type = float)
parser.add_argument('path_to_dataset', type = str)
args = parser.parse_args()

def read_file(file_name) -> list:
    """
    Read a file with movies information. Return a list with two
    arguments: movie name, movie location.
    """
    with open(file_name, 'r', encoding = 'UTF-8') as file:
        read_file = file.readlines()
    read_file = [element.strip().split("\t") for element in read_file if element.startswith('"')]
    for element in read_file:
        while '' in element:
            element.remove('')
    return read_file

def calculate_distance(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    """
    Calculate distance between two locations.
    """
    earth = 6371e3
    lat1 = latitude1 * math.pi / 180
    lat2 = latitude2 * math.pi / 180
    delta1 = (latitude2 - latitude1) * math.pi / 180
    delta2 = (longitude2 - longitude1) * math.pi / 180
    number1 = (math.sin(delta1/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(delta2/2))**2
    number2 = 2 * math.atan2(math.sqrt(number1), math.sqrt(1-number1))
    distance = (earth * number2) / 1000
    return round(distance, 3)

def find_top_ten(year: int, my_location: tuple, movies_list: list) -> list:
    """
    Find top ten closest locations to your location. Return a dictionary
    where key is a location and value is a number of movies filmed there.
    """
    coordinates = {}
    geolocator = Nominatim(user_agent="https://www.openstreetmap.org/copyright")
    for point in movies_list:
        if f'({year})' in point[0]:
            if '(' in point[1]:
                point[1] = point[1].split('(')[:-1]
                point[1] = point[1][0].replace('\t', '')
            location = geolocator.geocode(point[1])
            counter = 1
            while location == None:
                point[1] = ', '.join(point[1].split(', ')[counter:])
                location = geolocator.geocode(point[1])
                counter += 1
            coord = calculate_distance(my_location[0], my_location[1], location.latitude, location.longitude)
            place = (point[1], location.latitude, location.longitude, coord)
            if place not in coordinates.keys():
                coordinates.update({place: 1})
            else:
                coordinates[place] += 1
    keys = list(coordinates.keys())
    keys.sort(key = lambda distance: distance[3])
    sorted_coordinates = {city: coordinates[city] for city in keys}
    return sorted_coordinates

def create_map(year: int, latitide: float, longitude: float, file_name: str):
    """
    Create a map with movies that were filmed closest to your location.
    """
    top_ten = find_top_ten(year, (latitide, longitude), read_file(file_name))
    if len(top_ten) > 10:
        top_ten = dict(list(top_ten.items())[:10])
    map = folium.Map(location=[latitide, longitude], zoom_start=10)
    myloc = folium.FeatureGroup(name = 'My location')
    myloc.add_child(folium.CircleMarker(location=[latitide, longitude],
                        radius=10,
                        popup="I am here!",
                        color = 'red',
                        fill_color = 'red',
                        fill_opacity=0.5))
    movies = folium.FeatureGroup(name="Movies")
    for key, value in top_ten.items():
        movies.add_child(folium.Marker(location=[key[1], key[2]],
                    popup = folium.Popup(f'<strong>{year}</strong> {value}' + ' movie' if value == 1 else f'<strong>{year}</strong> {value}' + ' movies', max_width = 100, min_width = 100),
                    icon=folium.Icon(icon="fa-video", prefix='fa')))
    map.add_child(myloc)
    map.add_child(movies)
    map.add_child(folium.LayerControl())
    map.save('Map_Movies.html')
create_map(args.year, args.latitude, args.longitude, args.path_to_dataset)