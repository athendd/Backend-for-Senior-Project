import spacy
from PineconeInteractor import PineconeInteractor
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearch:
    
    def __init__(self, search_query, user_city):
        self.search_query = search_query
        self.pinecone_interactor = PineconeInteractor('example_database')
        self.user_city = user_city
        
    """
    Checks to see if text only mentions a location (City or Place)

    Returns the name of the location if the text contains one else it returns nothing
    """
    def check_for_location(self):        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.search_query.strip())
        
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                return ent.text
            
        return None
            
    """
    Searches Pinecone database for k results that best match the given search query
    
    Returns the top k results from the given search query
    """
    def perform_search(self, top_k=100, advanced_filters = None):
        search_query_embedding = self.pinecone_interactor.get_text_embedding(self.search_query)
        
        location = self.check_for_location()
        if not location:
            location = self.user_city
            
        filter_dict = {"city": {"$eq": location}}
        
        if advanced_filters:
            for key, value in advanced_filters.items():
                if value is not None:
                    filter_dict[key] = value


        return self.pinecone_interactor.index.query(
            vector = search_query_embedding.tolist(),  
            top_k = top_k,
            filter = filter_dict,
            include_metadata = True
        )['matches']