from diskcache import Cache
from utils import get_coordinates_from_address
import os

cache = Cache('.places_cache')

import requests

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

def get_coordinates_from_address(address):
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(geocode_url, params=params)
    print(response.json())
    location = response.json()['results'][0]['geometry']['location']
    return location['lat'], location['lng']

def find_nearby_transit(lat, lng, radius=1000):
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,  # in meters
        'type': 'transit_station',  # can also use 'bus_station', 'train_station', 'subway_station'
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(places_url, params=params)
    results = response.json().get('results', [])
    transit_locations = [{
        'name': place['name'],
        'address': place.get('vicinity', ''),
        'location': place['geometry']['location']
    } for place in results]
    return transit_locations

# Example usage
address = '52 Hemenway Street, Boston, MA, 02115'
lat, lng = get_coordinates_from_address(address)
transit_stations = find_nearby_transit(lat, lng)

for station in transit_stations:
    print(f"{station['name']} - {station['address']}")


