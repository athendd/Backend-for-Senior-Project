from utils import get_coordinates_from_address
import requests
import math
import heapq
import os
from diskcache import Cache
from itertools import chain

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

cache = Cache('.places_cache')

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

def check_if_restaurant(place_types):
    if 'restaurant' in place_types and not ('lodging' in place_types or 'hotel' in place_types):
        return True
    
    return False

"""
Obtain the keys from each dictionary in a list of dictionaries
"""
def get_keys(dictionary):
    return list(dictionary.keys())

"""
Takes in two lists and returns a list of elements that were in both inputted lists
"""
def find_common_elements(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    common_elements = list(set1.intersection(set2))
    
    return common_elements

"""
Extract key info from place such as name, address, rating, and distance 
Returns: a dictionary of only key info about the place
"""
def get_info(place, lat, lon, sort_key):
    
    #Variable for distance between current address and place
    dist = None
    
    #Get distance between current address and place if place has a longitude and latitude
    if place['geometry']['location']['lat'] and place['geometry']['location']['lng']:
        dist = find_distance(lat, lon, place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        
    if sort_key == 'rating':  
        place_info = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'rating': place.get('rating'),
                    'distance': dist
                }
    else:
         place_info = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'distance': dist
                }
    
    return place_info

"""
Loop through amenities/necessities to see if current place matches any of them. If so,
get key info on place and add it to the amenity/necessity's list
"""
def get_amenities_or_necessities(place, search_list, keys):
    
    #List of the types for each place
    place_types = place.get('types', [])
    
    if place_types != []:
        common_elements = find_common_elements(keys, place_types)
        
        if common_elements != []:
            for common_element in common_elements:
                search_list[common_element].append(place)  

"""
Get the top 5 places for each amenity/necessity by rating or distance
Returns: a list of the top 5 places for each amentiy/necessity
"""
def get_top_k_places(places, lat, lon, sort_key):
    heap = []
    for idx, place in enumerate(places):
        info = get_info(place, lat, lon, sort_key)
        key = -1 * info[sort_key] if sort_key == 'distance' else info[sort_key]
        heapq.heappush(heap, (key, idx, info))
        
        if len(heap) > 5:
            heapq.heappop(heap)
    
    return [item[2] for item in sorted(heap, key = lambda x: x[0], reverse = True)]

def places_api_call(lat, lon):
    cache_key = f"{lat}_{lon}_Points of Interest"
    
    #Check if data is cached
    if cache_key in cache:
        return cache[cache_key]

    #Radius is set to approximately 10 miles in meters
    params = {
        'location': f'{lat},{lon}',
        'radius': 32186,
        'type': 'points of interest',
        'key': PLACES_API_KEY,
    }

    response = requests.get(BASE_PLACES_URL, params=params)
    data = response.json()

    if data['status'] != 'OK':
        raise RuntimeError(f"API error: {data['status']} - {data.get('error_message')}")
    
    #Save results to cache
    cache[cache_key] = data['results']
    return data['results']

"""
Loop through the places data and obtain corresponding list of values for each amenity and necessity
"""
def loop_through_places(places, amenities, necessities, lat, lon):
    print(places)
    amenity_keys = get_keys(amenities)
    necessity_keys = get_keys(necessities)
    
    for place in places:
        get_amenities_or_necessities(place, amenities, amenity_keys)
        get_amenities_or_necessities(place, necessities, necessity_keys)
        
    for amenity_key in amenity_keys:
        amenities[amenity_key] = get_top_k_places(amenities[amenity_key], lat, lon, 'rating')
    
    for necessity_key in necessity_keys:
        necessities[necessity_key] = get_top_k_places(necessities[necessity_key], lat, lon, 'distance')

"""
Starts process to obtain data from the Places API for both local amenities and necessities
"""
def fetch_all_data(address, amenities, necessities):
    lat, lon = get_coordinates_from_address(address)
    
    if lat is None or lon is None:
        raise ValueError('Invalid Address')
    
    places = places_api_call(lat, lon)
        
    loop_through_places(places, amenities, necessities, lat, lon)
    
#Have it take in an address in the future
def main():
    if not PLACES_API_KEY:
        raise EnvironmentError("Missing Google Places API key")
    
    address = '52 Hemenway Street, Boston, MA, 02115'
      
    local_amenities = {
        'restaurant': [],'park': [],
        'supermarket':[], 'gym':[], 'cafe': [], 'shopping_mall': []
    }
    
    local_necessities = {
        'hospital':[], 'bank': [], 'pharmacy': []
    }
    
    fetch_all_data(address, local_amenities, local_necessities)
    
    print(local_amenities['shopping_mall'])
        

if __name__ == "__main__":
    main()