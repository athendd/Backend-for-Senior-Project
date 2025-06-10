from Coordinates_Obtainer import get_coordinates_from_address
import requests
import math

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

def get_info(place, lat, lon):
    dist = None
    if place['geometry']['location']['lat'] and place['geometry']['location']['lng']:
        dist = find_distance(lat, lon, place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        
    place_info = {
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'rating': place.get('rating'),
                'distance': dist
            }
    
    return place_info
    
def get_place_data(places, check_operation, lat, lon):
    obtained_places = []
    for place in places:
        place_types = place.get('types', [])
        
        if check_operation == None:
            place_info = get_info(place, lat, lon)
            obtained_places.append(place_info)
        else:
            if check_operation(place_types):
                place_info = get_info(place, lat, lon)
                obtained_places.append(place_info)
            
    return obtained_places

def get_data(lat, lon, radius, place_type, operation):
    params = {
        'location': f'{lat},{lon}',
        'radius': radius,
        'type': place_type,
        'key': PLACES_API_KEY,
    }
             
    response = requests.get(BASE_PLACES_URL, params = params)
    data = response.json()
    
    if data['status'] == 'OK':
        return get_place_data(data['results'], operation, lat, lon)
    else:
        print(f"Error fetching places: {data['status']}")
        return None

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
        
        amenities_data = {}
        
        for local_amenity in local_amenities:
            
            if local_amenity == 'restaurant':
                amenities_data[local_amenity] = get_data(lat, lon, search_radius, local_amenity, check_if_restaurant)  
            else:
                amenities_data[local_amenity] = get_data(lat, lon, search_radius, local_amenity, check_if_restaurant)  
        
        print(amenities_data['restaurant'])
        
main()    
    

    
