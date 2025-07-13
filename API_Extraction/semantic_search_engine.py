import spacy
import re
from PineconeInteractor import PineconeInteractor

class SemanticSearch:
    
    def __init__(self, search_query, user_city):
        self.search_query = search_query
        self.pinecone_interactor = PineconeInteractor('example-database')
        self.user_city = user_city
        
    """
    Checks to see if text only mentions a location (City or Place)

    Returns a tuple where first value is true if search query only looks for place, second value returns the location value
    """
    def check_for_location_only_query(self):
        stripped_query = self.search_query.strip()
        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(stripped_query)

        zipcode_match = re.match(r'\d{5}(?:-\d{4})?', stripped_query)
        if zipcode_match:
            'zipcode', zipcode_match.group(0)

        address = self.contains_us_address_regex(stripped_query)
        if address != None:
            return 'address', address
        
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                return 'name', ent.text.strip()

        return None, self.user_city
    
    def contains_us_address_regex(self, stripped_query):
        pattern = r"\b\d+\s+[\w\s]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Boulevard|Blvd)\.?,\s*[\w\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b"
        
        address_search_pattern = re.search(pattern, stripped_query, re.IGNORECASE)
        if address_search_pattern:
            return address_search_pattern.match(0)
        
        return None
            
    """
    Searches Pinecone database for k results that best match the given search query
    
    Args:
        -top_k (int): Number of search results to return
        -advanced_filters (dic): Dictionary of the chosen advanced filtering feature
    
    Returns the top k results from the given search query
    """
    def search_for_properties(self, top_k=100, advanced_filters = None):
        if self.search_query.isspace():
            return []
        
        location_type, location = self.check_for_location_only_query()
        
        filter_dict = None
        if location_type == 'zipcode':
            filter_dict = {'zipcode': {'$eq': location}}
        elif location_type == 'address':
            filter_dict = {'address': {'$eq': location}}
        else:
            filter_dict = {'city': {'$eq': location}}   
                       
        if advanced_filters:
            for key, value in advanced_filters.items():
                if value is not None:
                    filter_dict[key] = value
                    
        search_query_embedding = self.pinecone_interactor.get_text_embedding(self.search_query)
        return self.pinecone_interactor.index.query(
            vector = search_query_embedding.tolist(),
            top_k = top_k,
            filter = filter_dict,
            include_metadata = True
        )['matches']
            
search_query = '02110'
semantic_search = SemanticSearch(search_query, 'New York')
one = semantic_search.search_for_properties()
print(one)