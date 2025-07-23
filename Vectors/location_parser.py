import spacy
import re
from place_misspeller import PlaceMisspeller

class LocationParser:
    
    zipcode_pattern = re.compile(r'\d{5}(?:-\d{4})?$')
    address_pattern = re.compile(
        r"\d{3,6} [A-Za-z]+(?: [A-Za-z]+)*, [A-Za-z ]+, [A-Z]{2} \d{4}",
        re.IGNORECASE
    )
    
    def __init__(self, place_misspeller: PlaceMisspeller, user_city = None):
        self.nlp = spacy.load("en_core_web_sm") 
        self.user_city = user_city
        if self.user_city == None:
            self.user_city = 'Boston'
        self.place_misspeller = place_misspeller

    def check_for_location_only_query(self, stripped_query):       
        if self.is_zipcode(stripped_query):
            return 'zipcode', stripped_query

        address = self.extract_address(stripped_query)
        if address:
            return 'address', address
        
        corrected_query = self._correct_possible_places(stripped_query)
        doc = self.nlp(corrected_query)

        for ent in doc.ents:
            if ent.label_ == 'GPE':
                place_name = ent.text.strip()
                if self.place_misspeller.place_exists(place_name):
                    return 'name', place_name

        return None, self.user_city

    def _correct_possible_places(self, text):
        candidates = self.place_misspeller.get_place_candidates(text)
        corrected_text = text
        for candidate in sorted(candidates, key=len, reverse=True):  
            corrected = self.place_misspeller.correct_place(candidate)
            if corrected != None:
                corrected_text = corrected_text.replace(self.place_misspeller.capitalize_name(candidate), corrected)
                break               
        
        return corrected_text

    def check_place(self, place):
        if place in self.places:
            return True
        
        return False

    @staticmethod
    def is_zipcode(text):
        return bool(LocationParser.zipcode_pattern.fullmatch(text.strip()))

    @staticmethod
    def extract_address(text):
        match = LocationParser.address_pattern.search(text)
        return match.group(0) if match else None