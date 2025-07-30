from .pinecone_interactor import PineconeInteractor
from .location_parser import LocationParser
from .search_analyzer import SearchAnalyzer
from utils.utils import get_city_from_zipcode, get_city_zip_from_address
# python -m Vectors.semantic_search_engine - run that when testing

class SemanticSearch:
    
    def __init__(self, pinecone_interactor: PineconeInteractor, location_parser: LocationParser, search_analyzer: SearchAnalyzer, top_k = 100):
        self.pinecone_interactor = pinecone_interactor
        self.location_parser = location_parser
        self.search_analyzer = search_analyzer
        self.top_k = top_k
        self.zero_vector = [0.0] * 384
        self.advanced_filters = {}
            
    """
    Searches Pinecone database for k results that best match the given search query
    
    Args:
        -top_k (int): Number of search results to return
        -advanced_filters (dic): Dictionary of the chosen advanced filtering feature
    
    Returns the top k results from the given search query and the updated advanced filters dictionary
    """
    def search_for_properties(self, search_query, advanced_filters = {}):
        self.advanced_filters = advanced_filters
        
        stripped_search_query = search_query.strip()
        
        #If search query only has spaces
        if not stripped_search_query:
            return []
                
        location_type, location = self.location_parser.check_for_location_only_query(stripped_search_query)
        location_only = stripped_search_query.lower() in location.lower()
                
        self.create_filter_dict(location_type, location)
        
        print(self.advanced_filters)
        
        if location_only:
            search_result = self.pinecone_interactor.perform_search(self.zero_vector, self.top_k, self.advanced_filters)
        else:
            self.advanced_filters = self.search_analyzer.update_filters_dict(search_query, self.advanced_filters, location)
            search_query_embedding = self.pinecone_interactor.embedder.encode(stripped_search_query)
            search_result = self.pinecone_interactor.perform_search(search_query_embedding, self.top_k, self.advanced_filters)
        
        return self.convert_strs_to_ints(search_result), self.advanced_filters
    
    def create_filter_dict(self, location_type, location):
        if location_type == 'zipcode':
            self.advanced_filters['zipcode'] = location
            self.advanced_filters['city'] = get_city_from_zipcode(location)
        elif location_type == 'address':
            self.advanced_filters['address'] = location
            city, zipcode = get_city_zip_from_address(location)
            self.advanced_filters['city'] = city
            self.advanced_filters['zipcode'] = zipcode
        else:
            self.advanced_filters['city'] = location
            
    def get_filters_dict(self):
        return self.advanced_filters
    
    @staticmethod
    def convert_strs_to_ints(list_strs):
        int_list = []
        for s in list_strs:
            int_list.append(int(s))
            
        return int_list   
    
""" 
advanced_filters = {
        'property_type': None,
        'neighborhood_type': None,
        'num_beds': None,
        'num_baths': None,
        'move_in_date': None,
        'lease_term': None,
        'monthly_rent': None,
        'square_footage': None,
        'year_built': None,
        'min_age': {
            '$lte': 32
        },
        'max_age':
            {
                '$gte': 21
            },
        'pet_policy': None,
        'utilities_included':None,
        'washer': None,
        'dryer': None,
        'min_occupants': None,
        'max_occupants': None,
        'parking_spaces': None,
        'garage': None,
        'pool': None,
        'ac': None,
        'basement': None,
        'yard': None,
        'recently_renovated': None,
        'average_rating': None
}
"""