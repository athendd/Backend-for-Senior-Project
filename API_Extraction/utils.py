import requests
from geopy.geocoders import Nominatim

"""
Converts a given address into latitude and longitude coordinates
"""
def get_coordinates_from_address(address):
    geolocator = Nominatim(user_agent="LeaseLink")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None
    

