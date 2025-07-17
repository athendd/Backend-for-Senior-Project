import os
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

pinecone_api_key = os.environ.get('PINECONE_API_KEY')

class PineconeInteractor:
    
    def __init__(self, index_name, vector_dimension = 768, similarity_metric = 'cosine'):
        self.pc = Pinecone(api_key=pinecone_api_key, environment='example-environment')
        index_names = [index["name"] for index in self.pc.list_indexes()]
        
        if index_name not in index_names:
            self._create_pinecone_index(index_name, vector_dimension, similarity_metric)
        self.index_name = index_name
        self.index = self.pc.Index(index_name)
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-albert-small-v2') 
        
    """
    Creates a pinecone index
    
    Args:
        -index_name (str): Name of the index to be created
        -vector_dimension (int): Dimensions of the index
        -similarity_metric (str): Metric to compare vectors in the vector database
    """
    def _create_pinecone_index(self, index_name, vector_dimension, similarity_metric):
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
        -mysql_id (int): MySQL id for the given property
        -property_dic (dic): Dictionary containing all relevant information on a property
    """
    def upload_vector(self, mysql_id, property_dic):
        property_vector = self._create_property_vector(property_dic)
        metadata_dic = self._create_metadata_dictionary(mysql_id, property_dic)
        
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
        metadata = response.vectors[id].metadata
        
        return metadata
    
    """
    Gets the vector for a given property based on the given id
    
    Args:
        -id (str): mysql_id of the property
        
    Returns the vector of the property
    """
    def get_vector(self, id):
        res = self.index.fetch(ids=[id])

        if id in res.vectors:    
            return res.vectors[id].values
        
        return None
    
    """
    Creates the vector representation of the property
    
    Args:
        -property_dic (dic): Dictionary containing all relevant information on a property
        
    Returns: The vector representaiton of the given property
    
    Add weights later on
    """
    def _create_property_vector(self, property_dic):
        combined_text = f"""
        {property_dic['description']}. Located in {property_dic['city']}. {property_dic['number_of_beds']}-bedroom,
        {property_dic['number_of_baths']}-baths {property_dic['property_type']}. Has {property_dic['number_of_floors']} floors. 
        Rent costs ${property_dic['monthly_rent']} a month.
        Built in the year {property_dic['year_built']}. In a {property_dic['neighborhood_type']} neighborhood. Can have between 
        {property_dic['min_occupants']} and {property_dic['max_occupants']} occupants. Recommended for people between the ages of
        {property_dic['min_age']} and {property_dic['max_age']}. 
        """

        combined_text += self.square_footage_text(property_dic['property_type'], property_dic['square_footage'])
        combined_text += self.handicap_accessible_text(property_dic['handicap_accessible'])
        combined_text += self.smoking_policy_text(property_dic['smoking_policy'])
        combined_text += self.utilities_text(property_dic['utilities_included'])
        combined_text += self.basement_text(property_dic['basement'])
        combined_text += self.recently_renovated_text(property_dic['recently_renovated'])
        combined_text += self.pet_policy_text(property_dic['pet_policy'])
        
        boolean_cols = [
            'washer', 'dryer', 'ac', 'heating', 'garage', 'office', 'dishwasher', 'yard', 'balcony', 'fireplace', 'patio',
            'ev_charging', 'hardwood_floors', 'fitness_center', 'pool'
            ]
        
        combined_text += 'Has '
        for boolean_col in boolean_cols:
            col_value = property_dic.get(boolean_col, False)
            
            if col_value:
                combined_text += f'{col_value}, '
        
        #Replace last comma with period
        parts = combined_text.rsplit(',', 1)
        combined_text = parts[0] + '.'
        
        combined_text += self.transit_score_text(property_dic['transit_score'])
        combined_text += self.bike_score_text(property_dic['bike_score'])
        combined_text += self.walk_score_text(property_dic['walk_score'])
        
        vector = self.get_text_embedding(combined_text)
        
        return vector
    
    """
    Creates a numerical representation or embedding of the given text
    
    Args:
        -text (str): A piece of text
        
    Returns the numerical representation or embedding of the text
    """
    def get_text_embedding(self, text):
        return self.embedding_model.encode([text])[0].tolist()
    
    def _create_metadata_dictionary(self, mysql_id, property_dic):
        return {
        'mysql_id': mysql_id,
        'property_type': property_dic['property_type'],
        'neighborhood_type': property_dic['neighborhood_type'],
        'address': property_dic['address'],
        'city': property_dic['city'],
        'zipcode': property_dic['zipcode'],
        'latitude': property_dic['latitude'],
        'longitude': property_dic['longitude'],
        'num_beds': property_dic['number_of_beds'],
        'num_baths': property_dic['number_of_baths'],
        'move_in_date': property_dic['move_in_date'],
        'lease_term': property_dic['lease_term'],
        'monthly_rent': property_dic['monthly_rent'],
        'square_footage': property_dic['square_footage'],
        'year_built': property_dic['year_built'],
        'min_age': property_dic['min_age'],
        'max_age': property_dic['max_age'],
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
        
    def handicap_accessible_text(self, handicap_accessible):
        if handicap_accessible:
            return 'Is handicap accessible. '
        else:
            return ''
        
    def smoking_policy_text(self, smoking_policy):
        if smoking_policy:
            return 'Smoking is allowed. '
        else:
            return ''
            
    def utilities_text(self, utilities):
        if utilities:
            return 'Utilities are included. '
        else:
            return ''
            
    def basement_text(self, basement):
        if basement == 'Finished':
            return 'Has a finished basement. '
        elif basement == 'Unfinished':
            return 'Has an unfinished basement. '
        else:
            return ''
    
    def recently_renovated_text(self, recently_renovated):
        if recently_renovated:
            return 'Was recently renovated. '
        else:
            return ''
        
    def pet_policy_text(self, pet_policy):
        if pet_policy: 
            return 'Pets are allowed. '
        else:
            return ''
        
    def square_footage_text(self, property_type, square_footage):
        if property_type == 'apartment':
            if square_footage < 600:
                return 'Very little space. '
            elif 600 <= square_footage < 1000:
                return 'Average amount of space. '
            else:
                return 'A lot of space. '
        else:
            if square_footage < 1000:
                return 'Very little space. '
            elif 1000 <= square_footage < 2500:
                return 'Average amount of space. '
            else:
                return 'A lot of space. '
    
    def transit_score_text(self, transit_score):
        if 0 <= transit_score < 21:
            return 'Public transportation is very limited in this area. '
        elif 21 <= transit_score < 41:
            return 'Transit options are available but not very convenient. '
        elif 41 <= transit_score < 61:
            return 'The area has a fair level of public transportation. '
        elif 61 <= transit_score < 81:
            return 'Public transit is reliable and fairly accessible. '
        else:
            return 'Excellent public transportation with easy access to buses or trains. '
        
    def bike_score_text(self, bike_score):
        if 0 <= bike_score < 21:
            return 'This neighborhood is not suitable for biking. '
        elif 21 <= bike_score < 41:
            return 'Biking is possible, but infrastructure is lacking. '
        elif 41 <= bike_score < 61:
            return 'The area is moderately bike-friendly. '
        elif 61 <= bike_score < 81:
            return 'Biking is convenient with decent paths and lanes. '
        else:
            return 'The area is highly bikeable with excellent cycling infrastructure. '
        
    def walk_score_text(self, walk_score):
        if 0 <= walk_score < 21:
            return 'Almost everything requires a car — walking is not practical here.'
        elif 21 <= walk_score < 41:
            return 'Some places are walkable, but most errands require a vehicle.'
        elif 41 <= walk_score < 61:
            return 'The area is somewhat walkable, with some amenities nearby.'
        elif 61 <= walk_score < 81:
            return 'Many daily errands can be done on foot.'
        else:
            return 'Extremely walkable — most shops and services are within walking distance.'