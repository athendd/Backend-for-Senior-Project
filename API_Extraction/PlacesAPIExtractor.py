from utils import get_coordinates_from_address
import requests
import math
import heapq
import os
from diskcache import Cache
import time
from enum import Enum

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

cache = Cache('.places_cache')

class PlaceType(Enum):
    #Amenities
    RESTAURANT = "restaurant"
    PARK = "park"
    SUPERMARKET = "supermarket"
    GYM = "gym"
    CAFE = "cafe"
    SHOPPING_MALL = "shopping_mall"
    
    #Necessities
    HOSPITAL = "hospital"
    BANK = "bank"
    PHARMACY = "pharmacy"

def find_distance(lat1, lon1, lat2, lon2):
    #Radius of the Earth in miles
    radius = 3958.8
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    diff_lon = lon2_rad - lon1_rad
    diff_lat = lat2_rad - lat1_rad
    
    #Haversine formula
    a = math.sin(diff_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(diff_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = radius * c
    
    return round(dist, 2)

class PlacesAPIExtractor:
    
    def __init__(self, lat, lon, search_radius, top_k = 5):
        self.lat = lat
        self.lon = lon
        self.search_radius = search_radius
        self.is_amenity = False
        self.check_operation = False
        self.top_k = top_k
        
        self.local_amenities = [
            PlaceType.RESTAURANT, PlaceType.PARK,
            PlaceType.SUPERMARKET, PlaceType.GYM,
            PlaceType.CAFE, PlaceType.SHOPPING_MALL
        ]

        self.local_necessities = [
            PlaceType.HOSPITAL, PlaceType.BANK, PlaceType.PHARMACY
        ]
        
    """
    Process to obtain data from the Places API for both local amenities and necessities
    """
    def fetch_all_data(self):
        
        if not PLACES_API_KEY:
            raise EnvironmentError("Missing Google Places API key")
        
        if self.lat is None or self.lon is None:
            raise ValueError('Invalid Address')
        
        self.is_amenity = True
        amenities_data = {
            a.value: self.get_place_data(a.value)
            for a in self.local_amenities
        }
       
        self.is_amenity = False 
        necessities_data = {
            n.value: self.get_place_data(n.value)
            for n in self.local_necessities
        }
        
        return amenities_data, necessities_data
    
    def get_place_data(self, place_type):
        places = self.get_api_data(place_type)
        
        if places is not None:
            if self.is_amenity:
                if place_type == 'restaurant':
                    places = [place for place in places if self.check_if_restaurant(place.get('types', []))]
                return self.get_top_k_places(places, sort_key='rating')
            else:
                return self.get_top_k_places(places, sort_key='distance')
        else:
            return []
     
    def get_info(self, place):
        dist = None
        if place['geometry']['location']['lat'] and place['geometry']['location']['lng']:
            dist = find_distance(self.lat, self.lon, place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        
        place_info = {
            'name': place.get('name', 'Unkown'),
            'address': place.get('vicinity', 'Unkown'),
            'distance': dist
            }
        if self.is_amenity:
            place_info['rating'] = place.get('rating', 0)
            
        return place_info 

    def get_top_k_places(self, places, sort_key):
        heap = []
        for idx, place in enumerate(places):
            info = self.get_info(place)
            key = -1 * info[sort_key] if sort_key == 'distance' else info[sort_key]
            heapq.heappush(heap, (key, idx, info))
            
            if len(heap) > self.top_k:
                heapq.heappop(heap)
        
        return [item[2] for item in sorted(heap, key = lambda x: x[0], reverse = True)]

    """
    Obtains data from Places API for current place_type
    """
    def get_api_data(self, place_type):
        cache_key = f"{self.lat:.5f}_{self.lon:.5f}_{self.search_radius}_{place_type}"
        
        #Check if data is cached
        if cache_key in cache:
            return cache[cache_key]

        params = {
            'location': f'{self.lat},{self.lon}',
            'radius': self.search_radius,
            'type': place_type,
            'key': PLACES_API_KEY,
        }
        
        all_results = []
        
        while True:
            response = requests.get(BASE_PLACES_URL, params=params)
            data = response.json()

            if data['status'] == 'OK':
                raise RuntimeError(f"API error: {data['status']} - {data.get('error_message')}")
            
            results = data.get('results', [])
            all_results.extend(results)
            
            next_token = data.get('next_page_token')
            
            if not next_token:
                break
            
            time.sleep(2)
            params = {
                'pagetoken': next_token,
                'key': PLACES_API_KEY
            }
            
        #Save results to cache
        cache[cache_key] = data['results']
        return data['results']
    
    def check_if_restaurant(self, place_types):
        return 'restaurant' in place_types and 'lodging' not in place_types and 'hotel' not in place_types
    
    
"""
Run and test the PlacesAPIExtractor class
"""    

address = '52 Hemenway Street, Boston, MA, 02115'

lat, lon = get_coordinates_from_address(address)

placesAPIExtractor = PlacesAPIExtractor(lat, lon, 16093)

amenities, necessities = placesAPIExtractor.fetch_all_data()

print(amenities['restaurant'])
    
