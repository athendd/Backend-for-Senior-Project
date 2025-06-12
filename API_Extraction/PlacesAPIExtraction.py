from Coordinates_Obtainer import get_coordinates_from_address
import requests
import math
import heapq
import json
import os
from diskcache import Cache

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

def get_amenity_info(amenity, lat, lon):
    dist = None
    if amenity['geometry']['location']['lat'] and amenity['geometry']['location']['lng']:
        dist = find_distance(lat, lon, amenity['geometry']['location']['lat'], amenity['geometry']['location']['lng'])
        
    amenity_info = {
                'name': amenity.get('name'),
                'address': amenity.get('vicinity'),
                'rating': amenity.get('rating'),
                'distance': dist
            }
    
    return amenity_info

def get_necessity_info(necessity, lat, lon):
    dist = None
    if necessity['geometry']['location']['lat'] and necessity['geometry']['location']['lng']:
        dist = find_distance(lat, lon, necessity['geometry']['location']['lat'], necessity['geometry']['location']['lng'])
        
    necessity_info = {
                'name': necessity.get('name'),
                'address': necessity.get('vicinity'),
                'distance': dist
            }
    
    return necessity_info

def get_top_k_places(places, lat, lon, info_extractor, sort_key, k = 5):
    heap = []
    for idx, place in enumerate(places):
        info = info_extractor(place, lat, lon)
        key = -1 * info[sort_key] if sort_key == 'distance' else info[sort_key]
        heapq.heappush(heap, (key, idx, info))
        
        if len(heap) > k:
            heapq.heappop(heap)
    
    return [item[2] for item in sorted(heap, key = lambda x: x[0], reverse = True)]

def get_data(lat, lon, radius, place_type):
    cache_key = f"{lat:.5f}_{lon:.5f}_{radius}_{place_type}"
    
    #Check if data is cached
    if cache_key in cache:
        return cache[cache_key]

    params = {
        'location': f'{lat},{lon}',
        'radius': radius,
        'type': place_type,
        'key': PLACES_API_KEY,
    }

    response = requests.get(BASE_PLACES_URL, params=params)
    data = response.json()

    if data['status'] != 'OK':
        raise RuntimeError(f"API error: {data['status']} - {data.get('error_message')}")
    
    # Save results to cache
    cache[cache_key] = data['results']
    return data['results']
    
def get_amenity_data(lat, lon, radius, place_type, check_operation):
    amenities = get_data(lat, lon, radius, place_type)
    
    if amenities != None:
        if check_operation != None:
            amenities = [a for a in amenities if check_operation(a.get('types', []))]
        return get_top_k_places(amenities, lat, lon, get_amenity_info, sort_key='rating')
    else:
        return []
    
def get_necessity_data(lat, lon, radius, place_type):
    necessities = get_data(lat, lon, radius, place_type)
    
    if necessities != None:
        return get_top_k_places(necessities, lat, lon, get_necessity_info, sort_key='distance')
    else:
        return []
    
def fetch_all_data(address, radius, amenities, necessities):
    lat, lon = get_coordinates_from_address(address)
    
    if lat is None or lon is None:
        raise ValueError('Invalid Address')
    
    amenities_data = {
        a: get_amenity_data(lat, lon, radius, a, check_if_restaurant if a == 'restaurant' else None)
        for a in amenities
    }
    
    necessities_data = {
        n: get_necessity_data(lat, lon, radius, n)
        for n in necessities
    }
    
    return amenities_data, necessities_data

#Have it take in address in the future
def main():
    if not PLACES_API_KEY:
        raise EnvironmentError("Missing Google Places API key")
    
    address = '52 Hemenway Street, Boston, MA, 02115'
      
    #Search 10 miles nearest to address
    search_radius = 16093
    local_amenities = [
        'restaurant','park',
        'supermarket', 'gym', 'cafe', 'shopping_mall'
    ]
    
    local_necessities = [
        'hospital', 'bank', 'pharmacy'
    ]
        
    amenities, necessities = fetch_all_data(address, search_radius, local_amenities, local_necessities)
    
    print(amenities['restaurant'])
    print(necessities['hospital'])
        
    #Have it return amenities and necessities data
        
main()    
    

    
