from Coordinates_Obtainer import get_coordinates_from_address
import requests

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = "AIzaSyA6Dqu9ss0_gAUSMllyjxouj47bVPZbZeY"

def get_places(lat, lon, radius, place_type):
    params = {
        'location': f'{lat},{lon}',
        'radius': radius,
        'type': place_type,
        'key': PLACES_API_KEY,
    }
             
    response = requests.get(BASE_PLACES_URL, params = params)
    data = response.json()
    
    if data['status'] == 'OK':
        print(data['results'])
    else:
        print(f"Error fetching places: {data['status']}")

def main():
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    lat, lon = get_coordinates_from_address(address)
    
    if lat != None and lon != None:
        #Search 25 miles nearest to address
        search_radius = 40234
        local_amenities = [
            'restaurants','parks',
            'grocery stores', 'gyms', 'coffee shops', 'shopping centers'
        ]
        get_places(lat, lon, search_radius, local_amenities[0])
        
        
        
main()    
    

    
