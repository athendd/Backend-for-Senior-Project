import spacy
import re

class LocationParser:
    
    zipcode_pattern = re.compile(r'\d{5}(?:-\d{4})?$')
    address_pattern = re.compile(
        r"\d{3,6} [A-Za-z]+(?: [A-Za-z]+)*, [A-Za-z ]+, [A-Z]{2} \d{4}",
        re.IGNORECASE
    )
    
    def __init__(self, user_city):
        self.nlp = spacy.load("en_core_web_sm") 
        self.user_city = user_city

    def check_for_location_only_query(self, stripped_query):                
        if self.is_zipcode(stripped_query):
            return 'zipcode', stripped_query

        address = self.extract_address(stripped_query)
        if address:
            return 'address', address
        
        doc = self.nlp(stripped_query)
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                return 'name', ent.text.strip()

        return None, self.user_city

    @staticmethod
    def is_zipcode(text):
        return bool(LocationParser.zipcode_pattern.fullmatch(text.strip()))

    @staticmethod
    def extract_address(text):
        match = LocationParser.address_pattern.search(text)
        return match.group(0) if match else None
