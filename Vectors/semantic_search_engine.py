from pinecone_interactor import PineconeInteractor
from location_parser import LocationParser
from filter_builder import FilterBuilder

class SemanticSearch:
    
    def __init__(self, pinecone_interactor: PineconeInteractor, location_parser: LocationParser, filter_builder: FilterBuilder, top_k = 100):
        self.pinecone_interactor = pinecone_interactor
        self.location_parser = location_parser
        self.filter_builder = filter_builder
        self.top_k = top_k
        self.zero_vector = [0.0] * 768
            
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
                
        filter_dict = self.filter_builder.create_filter_dict(location_type, location, advanced_filters)
        
        if location_only:
            search_result = self.pinecone_interactor.perform_search(self.zero_vector, self.top_k, filter_dict)
        else:
            search_query_embedding = self.pinecone_interactor.embedder.encode(stripped_search_query)
            search_result = self.pinecone_interactor.perform_search(search_query_embedding, self.top_k, filter_dict)
            
        return search_result