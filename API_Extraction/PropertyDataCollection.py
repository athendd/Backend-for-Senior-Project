from utils import get_coordinates_from_address
import os
from LocalPlacesExtractor import LocalPlacesExtractor

BASE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

"""
Gets Walk Score API, local necessities/amenities, and local transporation data
"""
def execute_data_extraction(address):    
    lat, lon = get_coordinates_from_address(address)
    
    if lat is not None and lon is not None:
        
        #Run walk score api when it is setup
    
        if PLACES_API_KEY:
            #Search radius is given in meters 
            placesAPIExtractor = LocalPlacesExtractor(lat, lon, 16093)
            tran_and_places_data = placesAPIExtractor.fetch_all_data()
    
    return tran_and_places_data

if __name__ == '__main__':
    address = '52 Hemenway Street, Boston, MA, 02115'
    
    data = execute_data_extraction(address)
    
        
    

        
    