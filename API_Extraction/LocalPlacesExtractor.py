from utils import get_coordinates_from_address, find_distance
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
    
    #Local Transportation
    BUS = "bus_station"
    TRAIN = "train_station"
    SUBWAY = "subway_station"

class LocalPlacesExtractor:
    
    def __init__(self, lat, lon, search_radius, top_k = 5):
        self.lat = lat
        self.lon = lon
        self.search_radius = search_radius
        self.is_amenity = False
        self.is_tran = False
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
        
        self.local_transportation = [
            PlaceType.BUS, PlaceType.TRAIN, PlaceType.SUBWAY
        ]
        
    """
    Process to obtain data from the Places API for both local amenities and necessities
    """
    def fetch_all_data(self):
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
        
        self.is_tran = True
        local_tran_data = {
            t.value: self.get_place_data(t.value)
            for t in self.local_transportation
        }
        
        #Combine the amenities and necessities into one dictionary
        return amenities_data | necessities_data | local_tran_data
    
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
        
        if self.is_tran:
            place_info = {
            'name': place.get('name', 'Unkown'),
            'distance': dist
            }
            
        else:
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
            
            if data['status'] != 'OK':
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