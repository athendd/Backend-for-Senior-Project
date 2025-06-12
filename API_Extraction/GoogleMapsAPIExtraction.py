from Coordinates_Obtainer import get_coordinates_from_address
import requests
import math
import heapq

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = "AIzaSyDe6GsGguP9k4zBNHEE9hzozj2HGFGRPp0"

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

def get_amenity_data(amenities, lat, lon, check_operation):
    obtained_amenities = []
    for idx, amenity in enumerate(amenities):
        if check_operation == None:
            amenity_info = get_amenity_info(amenity, lat, lon)
            heapq.heappush(obtained_amenities, (amenity_info['rating'], idx, amenity_info))
        else:
            amenity_types = amenity.get('types', [])
            if check_operation(amenity_types):
                amenity_info = get_amenity_info(amenity, lat, lon)
                heapq.heappush(obtained_amenities, (amenity_info['rating'], idx, amenity_info))
                
        if len(obtained_amenities) > 5:
            heapq.heappop(obtained_amenities)

    return [item[2] for item in sorted(obtained_amenities, key = lambda x: x[0], reverse = True)]

def get_necessity_data(necessities, lat, lon):
    obtained_necessities = []
    for idx, necessity in enumerate(necessities):
        necessity_info = get_necessity_info(necessity, lat, lon)
        distance = necessity_info['distance'] * -1
        heapq.heappush(obtained_necessities, (distance, idx, necessity_info))
        
        if len(obtained_necessities) > 5:
            heapq.heappop(obtained_necessities)
        
    return [item[2] for item in sorted(obtained_necessities, key = lambda x: x[0], reverse = True)]

def get_data(lat, lon, radius, place_type):
    params = {
        'location': f'{lat},{lon}',
        'radius': radius,
        'type': place_type,
        'key': PLACES_API_KEY,
    }
             
    response = requests.get(BASE_PLACES_URL, params = params)
    data = response.json()
    if data['status'] == 'OK':
        return data['results']
    else:
        print(f"Error fetching places: {data['status']}")
        return None
    
def get_local_amenity_data(lat, lon, radius, place_type, operation):
    obtained_data = get_data(lat, lon, radius, place_type)
    
    if obtained_data != None:
        return get_amenity_data(obtained_data, lat, lon, operation)
        
    else:
        return []
    
def get_local_necessity_data(lat, lon, radius, place_type):
    obtained_data = get_data(lat, lon, radius, place_type)
    
    if obtained_data != None:
        return get_necessity_data(obtained_data, lat, lon)
    else:
        return []

def main():
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    lat, lon = get_coordinates_from_address(address)
    
    if lat != None and lon != None:
        
        #Search 10 miles nearest to address
        search_radius = 16093
        local_amenities = [
            'restaurant','park',
            'supermarket', 'gym', 'cafe', 'shopping_mall'
        ]
        
        local_necessities = [
            'hospital', 'bank', 'pharmacy'
        ]
        
        amenities_data = {}
        necessities_data = {}
        
        for local_amenity in local_amenities:
            if local_amenity == 'restaurant':
                amenities_data[local_amenity] = get_local_amenity_data(lat, lon, search_radius, local_amenity, check_if_restaurant)  
            else:
                amenities_data[local_amenity] = get_local_amenity_data(lat, lon, search_radius, local_amenity, check_if_restaurant)  
        
        for local_necessity in local_necessities:
            necessities_data[local_necessity] = get_local_necessity_data(lat, lon, search_radius, local_necessity)
            
        
        print(amenities_data['restaurant'])
        print(necessities_data)
        
main()    
    

    
