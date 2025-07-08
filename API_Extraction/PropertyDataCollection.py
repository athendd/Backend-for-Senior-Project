from utils import get_coordinates_from_address
import os
from PlacesAPIExtractor import PlacesAPIExtractor

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

"""
Gets Walk Score API, local necessities/amenities, and local transporation data
"""
def execute_data_extraction(address):    
    lat, lon = get_coordinates_from_address(address)
    
    if lat is None or lon is None:
        raise ValueError('Unable to obtain latitude or longitude from given address')
        
    #Run walk score api when it is setup
    
    if not PLACES_API_KEY:
        raise EnvironmentError("Missing Google Places API Key. Set 'GOOGLE_PLACES_API_KEY' in env.")
       
    #Search radius is given in meters 
    placesAPIExtractor = PlacesAPIExtractor(lat, lon, 16093)
    tran_and_places_data = placesAPIExtractor.fetch_all_data()
    
    return tran_and_places_data

if __name__ == '__main__':
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    try:
        data = execute_data_extraction(address)
    except EnvironmentError as e:
        print(e)  
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    print(data)
    
        
    

        
    