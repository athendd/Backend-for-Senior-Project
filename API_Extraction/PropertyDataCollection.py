from utils import get_coordinates_from_address
import os
from LocalPlacesExtractor import LocalPlacesExtractor

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

"""
Gets Walk Score API, local necessities/amenities, and local transporation data
"""
def execute_data_extraction(address):
    local_transporation_data = None
    local_places_data = None
    walk_score_api_data = None
    
    lat, lon = get_coordinates_from_address(address)
    
    if lat is not None and lon is not None:
        
        #Run walk score api when it is setup
    
        if PLACES_API_KEY:
            #Search radius is given in meters 
            placesAPIExtractor = LocalPlacesExtractor(lat, lon, 16093)
            local_places_data = placesAPIExtractor.fetch_all_data()
    
    return local_transporation_data, local_places_data, walk_score_api_data

if __name__ == '__main__':
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    tran, places, walk = execute_data_extraction(address)
        
    

        
    