from pinecone_interactor import PineconeInteractor
from location_parser import LocationParser

class SemanticSearch:
    
    def __init__(self, pinecone_interactor: PineconeInteractor, location_parser: LocationParser, top_k = 100):
        self.pinecone_interactor = pinecone_interactor
        self.location_parser = location_parser
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
            search_query_embedding = self.pinecone_interactor.embedder.encode(stripped_search_query)
            search_result = self.pinecone_interactor.perform_search(search_query_embedding, self.top_k, filter_dict)
        
        return self.convert_strs_to_ints(search_result)
    
    @staticmethod
    def create_filter_dict(location_type, location, advanced_filters):
        if location_type == 'zipcode':
            location_filter = {'zipcode': {'$eq': int(location)}}
        elif location_type == 'address':
            location_filter = {'address': {'$eq': location}}
        else:
            location_filter = {'city': {'$eq': location}}

        clean_advanced_filters = {
            key: value for key, value in (advanced_filters or {}).items() if value is not None
        }

        return {**location_filter, **clean_advanced_filters}
    
    @staticmethod
    def convert_strs_to_ints(list_strs):
        int_list = []
        for s in list_strs:
            int_list.append(int(s))
            
        return int_list   