from utils.utils import get_coordinates_from_address, get_city_zip_from_address
import os
from PlacesAPIExtractor import PlacesAPIExtractor
from WalkAPIExtraction import WalkScoreExtractor

PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

"""
Gets Walk Score API, local necessities/amenities, and local transporation data

Have it return Walk Score API Data when access to that API is available
"""
def execute_data_extraction(property_dic):    
    address = property_dic['address']
    
    lat, lon = get_coordinates_from_address(address)
    city, zipcode = get_city_zip_from_address(address)
    
    property_dic['latitude'] = lat
    property_dic['longitude'] = lon
    property_dic['city'] = city
    property_dic['zipcode'] = zipcode
        
    if lat is None or lon is None:
        raise ValueError('Unable to obtain latitude or longitude from given address')
        
    
    if not PLACES_API_KEY:
        raise EnvironmentError("Missing Google Places API Key. Set 'GOOGLE_PLACES_API_KEY' in env.")
       
    walk_score_extractor = WalkScoreExtractor()
    scores = walk_score_extractor.get_scores()
    
    if scores == None:
        raise ValueError('Unable to obtains scores from walk score api')
    
    
        
    #Search radius is given in meters 
    placesAPIExtractor = PlacesAPIExtractor(lat, lon, 16093, PLACES_API_KEY)
    tran_and_places_data = placesAPIExtractor.fetch_all_data()
    
    if tran_and_places_data == None:
        raise ValueError('Unable to obtain places data from places api')
    
    for key in scores.keys():
        property_dic[key] = scores[key]
        
    for key in tran_and_places_data.keys():
        property_key = key.replace('_', ' ')
        property_key += 's'
        
        property_dic[property_key] = tran_and_places_data[key]
        
    return property_dic