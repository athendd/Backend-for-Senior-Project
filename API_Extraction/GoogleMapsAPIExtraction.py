from Coordinates_Obtainer import get_coordinates_from_address
import requests

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = "AIzaSyDe6GsGguP9k4zBNHEE9hzozj2HGFGRPp0"

def find_distance(lat1, lon1, lat2, lon2):
    pass

def get_places(lat, lon, radius, place_type):
    params = {
        'location': f'{lat},{lon}',
        'radius': radius,
        'type': place_type,
        'key': PLACES_API_KEY,
        'fields': ['name', 'distance', 'rating']
    }
             
    response = requests.get(BASE_PLACES_URL, params = params)
    data = response.json()
    
    if data['status'] == 'OK':
        for place in data['results']:
            print(f"Restaurant Name: {place.get('name')}")
            print(f"Address: {place.get('vicinity')}")
            print(f"Rating: {place.get('rating')}")
            location = place['geometry']['location']
            print(location['lat'])
            print(location['lng'])
    else:
        print(f"Error fetching places: {data['status']}")

def main():
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    lat, lon = get_coordinates_from_address(address)
    
    if lat != None and lon != None:
        
        #Search 10 miles nearest to address
        search_radius = 16093
        local_amenities = [
            'restaurants','parks',
            'grocery stores', 'gyms', 'coffee shops', 'shopping centers'
        ]
        get_places(lat, lon, search_radius, 'restaurants')  
        
main()    
    

    
