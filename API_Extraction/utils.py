from geopy.geocoders import Nominatim
import math
import re

"""
Converts a given address into latitude and longitude coordinates
"""
def get_coordinates_from_address(address):
    try:
        geolocator = Nominatim(user_agent="LeaseLink")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error for address '{address}': {e}")
        return None, None
    
"""
Gets city and zipcode from a given address
"""
def get_city_zip_from_address(address):
    split_address = address.split(',')
    
    city = split_address[1].strip()
    
    zipcode = None
    zipcode_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
    
    if zipcode_match:
        zipcode = zipcode_match.group(0)
        
    print(city)
    print(zipcode)
        
    return city, zipcode

"""
Finds the distance between two places by using their corresponding latitudes and longitudes
"""
def find_distance(lat1, lon1, lat2, lon2):
    try:
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

    except Exception as e:
        print(f'Distance calculation error: {e}')
        return None

