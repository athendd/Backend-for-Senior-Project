import spacy
import re
from misspeller_fixer import MisspellerFixer

class LocationParser:
    zipcode_pattern = re.compile(r'\d{5}(?:-\d{4})?$')
    address_pattern = re.compile(r"\d{3,6} [A-Za-z]+(?: [A-Za-z]+)*, [A-Za-z ]+, [A-Z]{2} \d{4}", re.IGNORECASE)

    def __init__(self, places=None, user_city='Boston'):
        self.nlp = spacy.load("en_core_web_sm")
        self.places = places if places else ['Boston']
        self.user_city = user_city
        self.misspeller_fixer = MisspellerFixer(self.places)

    def check_for_location_only_query(self, search_query):
        zipcode = self.extract_zipcode(search_query)
        if zipcode:
            return 'zipcode', zipcode

        address = self.extract_address(search_query)
        if address:
            return 'address', address

        max_length = max(len(place.split()) for place in self.places)
        corrected_query = self.misspeller_fixer.correct_text(search_query, max_length)
        doc = self.nlp(corrected_query)
        
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                place = ent.text.strip()
                if place in self.places:
                    return 'city', place

        return None, self.user_city

    @staticmethod
    def extract_zipcode(text):
        match = LocationParser.zipcode_pattern.fullmatch(text.strip())
        return match.group() if match else None
    
    @staticmethod
    def extract_address(text):
        match = LocationParser.address_pattern.search(text)
        return match.group(0) if match else None