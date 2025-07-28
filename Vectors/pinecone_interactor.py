import os
from pinecone import Pinecone, ServerlessSpec
from embedder import Embedder
from vector_builder import PropertyVectorBuilder

pinecone_api_key = os.environ.get('PINECONE_API_KEY')

class PineconeInteractor:
        
    def __init__(self, index_name, vector_dimension = 384, similarity_metric = 'cosine'):
        self.pc = Pinecone(api_key=pinecone_api_key, environment='example-environment')
        
        if index_name not in [i['name'] for i in self.pc.list_indexes()]:
            self._create_index(index_name, vector_dimension, similarity_metric)
            
        self.index_name = index_name
        self.embedder = Embedder()
        self.property_vector_builder = PropertyVectorBuilder(self.embedder)
        self.index = self.pc.Index(index_name)
        
    """
    Creates a pinecone index
    
    Args:
        -index_name (str): Name of the index to be created
        -vector_dimension (int): Dimensions of the index
        -similarity_metric (str): Metric to compare vectors in the vector database
    """
    def _create_index(self, index_name, vector_dimension, similarity_metric):
        self.pc.create_index(
            name= index_name,
            dimension=vector_dimension,
            metric=similarity_metric,
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        
    def perform_search(self, vector, top_k, filter_dict):
        results = self.index.query(
                vector = vector,  
                top_k = top_k,
                filter = filter_dict,
                include_metadata = False
            )['matches']
        
        #Return only IDs
        return [result['id'] for result in results]  

    """
    Creates the embedding and metadata dictionary for the given property dic and then uploads them to the chosen Pinecone index
    
    Args:
        -mysql_id (str): MySQL id for the given property
        -property_dic (dict): Dictionary containing all relevant information on a property
    """
    def upload_vector(self, mysql_id, property_dic):
        property_vector = self.property_vector_builder.build(property_dic)
        metadata_dic = self._create_metadata(mysql_id, property_dic)
        
        self.index.upsert([{
        'id': mysql_id,
        'values': property_vector,
        'metadata': metadata_dic
        }])
        
    """
    Gets the metadata vector for a given property based on its id
    
    Args:
        -id (str): mysql_id of the property vector
        
    Returns the metadata dictionary for the property
    """
    def get_metadata(self, id):
        response = self.index.fetch(ids=[id])
        return response.vectors[id].metadata
            
    """
    Gets the vector for a given property based on the given id
    
    Args:
        -id (str): mysql_id of the property
        
    Returns the vector of the property
    """
    def get_vector(self, id):
        res = self.index.fetch(ids=[id])
        return res.vectors[id].values if id in res.vectors else None
    
    def _create_metadata(self, mysql_id, property_dic):
        return {
        'mysql_id': mysql_id,
        'property_type': property_dic['property_type'],
        'neighborhood_type': property_dic['neighborhood_type'],
        'address': property_dic['address'],
        'city': property_dic['city'],
        'zipcode': property_dic['zipcode'],
        'num_beds': property_dic['number_of_beds'],
        'num_baths': property_dic['number_of_baths'],
        'move_in_date': property_dic['move_in_date'],
        'lease_term': property_dic['lease_term'],
        'monthly_rent': property_dic['monthly_rent'],
        'square_footage': property_dic['square_footage'],
        'year_built': property_dic['year_built'],
        'max_age': property_dic['min_age'],
        'min_age': property_dic['max_age'],
        'pet_policy': property_dic['pet_policy'],
        'utilities_included': property_dic['utilities_included'],
        'washer': property_dic['washer'],
        'dryer': property_dic['dryer'],
        'min_occupants': property_dic['min_occupants'],
        'max_occupants': property_dic['max_occupants'],
        'parking_spaces': property_dic['parking_spaces'],
        'garage': property_dic['garage'],
        'pool': property_dic['pool'],
        'ac': property_dic['ac'],
        'basement': property_dic['basement'],
        'yard': property_dic['yard'],
        'recently_renovated': property_dic['recently_renovated'],
        'average_rating': property_dic['average_rating']
    }   