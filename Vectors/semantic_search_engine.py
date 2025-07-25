from pinecone_interactor import PineconeInteractor
from location_parser import LocationParser
from misspeller_fixer import MisspellerFixer
from search_analyzer import SearchAnalyzer

class SemanticSearch:
    
    def __init__(self, pinecone_interactor: PineconeInteractor, location_parser: LocationParser, search_analyzer: SearchAnalyzer, top_k = 100):
        self.pinecone_interactor = pinecone_interactor
        self.location_parser = location_parser
        self.search_analyzer = search_analyzer
        self.top_k = top_k
        self.zero_vector = [0.0] * 384
            
    """
    Searches Pinecone database for k results that best match the given search query
    
    Args:
        -top_k (int): Number of search results to return
        -advanced_filters (dic): Dictionary of the chosen advanced filtering feature
    
    Returns the top k results from the given search query
    """
    def search_for_properties(self, search_query, advanced_filters = None):
        stripped_search_query = search_query.strip()
        
        #If search query only has spaces
        if not stripped_search_query:
            return []
                
        location_type, location = self.location_parser.check_for_location_only_query(stripped_search_query)
        location_only = stripped_search_query.lower() in location.lower()
                
        filter_dict = self.create_filter_dict(location_type, location, advanced_filters)
        
        if location_only:
            search_result = self.pinecone_interactor.perform_search(self.zero_vector, self.top_k, filter_dict)
        else:
            updated_filter_dict = self.search_analyzer.update_filters_dict(search_query, filter_dict, location)
            print(updated_filter_dict)
            search_query_embedding = self.pinecone_interactor.embedder.encode(stripped_search_query)
            search_result = self.pinecone_interactor.perform_search(search_query_embedding, self.top_k, updated_filter_dict)
        
        return self.convert_strs_to_ints(search_result)
    
    @staticmethod
    def create_filter_dict(location_type, location, advanced_filters):
        updated = {}
        if location_type == 'zipcode':
            updated['zipcode'] = int(location)
        elif location_type == 'address':
            updated['address'] = location
        elif location_type == 'city':
            updated['city'] = location

        for k, v in advanced_filters.items():
            if v is not None:
                updated[k] = v

        return updated
    
    @staticmethod
    def convert_strs_to_ints(list_strs):
        int_list = []
        for s in list_strs:
            int_list.append(int(s))
            
        return int_list   
    
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
        'min_age': None,
        'max_age': None,
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
