import spacy
import re
from PineconeInteractor import PineconeInteractor

class SemanticSearch:
    
    def __init__(self, search_query, user_city):
        self.search_query = search_query
        self.pinecone_interactor = PineconeInteractor('final-database')
        self.user_city = user_city
        self.nlp = spacy.load("en_core_web_sm") 
        self.zipcode_pattern = re.compile(r'\d{5}(?:-\d{4})?$')
        self.zero_vector = [0.0] * 768
        #Change 4 to 5 once you fix the issue
        self.address_pattern = re.compile(
            r"\d{3,6} [A-Za-z]+(?: [A-Za-z]+)*, [A-Za-z ]+, [A-Z]{2} \d{4}",
            re.IGNORECASE
        )

    """
    Checks to see if text only mentions a location (City or Place)

    Returns a tuple where first value is true if search query only looks for place, second value returns the location value
    """
    def check_for_location_only_query(self):
        stripped_query = self.search_query.strip()
                
        zipcode_match = re.match(self.zipcode_pattern, stripped_query)
        if zipcode_match != None:
            return 'zipcode', zipcode_match.group(0)

        address = self.contains_us_address_regex(stripped_query)
        if address != None:
            return 'address', address
        
        doc = self.nlp(stripped_query)
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                return 'name', ent.text.strip()

        return None, self.user_city
    
    def contains_us_address_regex(self, stripped_query):        
        address_search_pattern = re.search(self.address_pattern, stripped_query)
        if address_search_pattern != None:
            return address_search_pattern.group(0)
        
        return None
    
    def create_filter_dict(self, location_type, location, advanced_filters):
        filter_dict = None
        if location_type == 'zipcode':
            location = float(location)
            filter_dict = {'zipcode': {'$eq': location}}
        elif location_type == 'address':
            filter_dict = {'address': {'$eq': location}}
        else:
            filter_dict = {'city': {'$eq': location}}   
                       
        if advanced_filters:
            for key, value in advanced_filters.items():
                if value is not None:
                    filter_dict[key] = value
                    
        return filter_dict
            
    """
    Searches Pinecone database for k results that best match the given search query
    
    Args:
        -top_k (int): Number of search results to return
        -advanced_filters (dic): Dictionary of the chosen advanced filtering feature
    
    Returns the top k results from the given search query
    """
    def search_for_properties(self, top_k=100, advanced_filters = None):
        #If search query only has spaces
        if not self.search_query.strip():
            return []
        
        location_only = False
        
        location_type, location = self.check_for_location_only_query()
        
        if len(location) == len(self.search_query.strip()):
            location_only = True
        
        filter_dict = self.create_filter_dict(location_type, location, advanced_filters)
        
        if location_only:
            search_result = self.pinecone_interactor.perform_search(self.zero_vector, top_k, filter_dict)
        else:
            search_query_embedding = self.pinecone_interactor.get_text_embedding(self.search_query)
            search_result = self.pinecone_interactor.perform_search(search_query_embedding, top_k, filter_dict)
            
        return search_result
