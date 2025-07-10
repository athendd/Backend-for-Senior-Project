from pinecone import Pinecone, ServerlessSpec
import logging
import spacy
import re
import os
import pandas as pd
from sentence_transformers import SentenceTransformer

pinecone_api_key = os.environ.get('PINECONE_API_KEY')

pc = Pinecone(api_key = pinecone_api_key, environment='example-environment')

embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

"""
Uploader for example database
"""
def example_uploader(df):
    index_name = 'example-database'
    create_pinecone_index(index_name, 384, 'cosine')
    
    index = pc.Index(index_name)

    for i, row in df.iterrows():
        original = row.to_dict()
        upload_property_vectory(index, original, f'mysql_id_{i}')

"""
Creates an index on Pinecone if it doesn't already exist
"""
def create_pinecone_index(index_name, vector_dimension, similarity_metric):
    if index_name not in pc.list_indexes():
        pc.create_index(
            name = index_name,
            dimension = vector_dimension,
            metric = similarity_metric,
            spec = ServerlessSpec(cloud = 'aws', region = 'us-east-1')
        )
        
"""
Uploads a given property to the Pinecone vector database

Alter in the future to remove city and zipcode add on
"""
def upload_property_vectory(index, property_dic, mysql_id):
    combined_text = create_text(property_dic)
    combined_text += get_text_representations(property_dic)
    text_embedding = get_text_embedding(combined_text)    
    
    metadata = create_metadata(mysql_id, property_dic)
    
    index.upsert([
        {
            'id': mysql_id,
            'values': text_embedding.tolist(),
            'metadata': metadata
        }
    ]) 
    
"""
SentenceTransformer to perform text embedding on combined text
"""
def get_text_embedding(text):
    
    return embedding_model.encode([text])[0]
    
"""
Turns the address, description, property type, and neighborhood type into text
"""
def create_text(property_dic):
    combined_text = (
        f"{property_dic['description']}. Located at {property_dic['address']}. "
        f"Neighborhood: {property_dic['neighborhood_type']}. Property type: {property_dic['property_type']}. "
    )
    
    return combined_text

"""
Get text representations for all numerical, categorical, and boolean columns
"""
def get_text_representations(property_dic):
    features = []
    
    has_a_columns = ['washer', 'dryer', 'garage', 'dishwasher',
                           'yard', 'balcony', 'fireplace', 'patio',
                           'fitness_center', 'pool']
    has_columns = ['ac', 'heating', 'ev_charging', 'hardwood_floors']
    
    
    if property_dic['smoking_policy'] == True:
        features.append('Allows smoking')
        
    if property_dic['office'] == True:
        features.append('Has an office')
    
    if property_dic['utilities_included'] == True:
        features.append('Includes utilities')
    
    if property_dic['handicap_accessible'] == True:
        features.append('Is handicap accessible')
        
    if property_dic['recently_renovated'] == True:
        features.append('Was recently renovated')
    
    features.append(get_basement_text(property_dic['basement']))
    
    for col in has_a_columns:
        if property_dic[col] == True:
            text_to_append = f'Has a {col}'
            text_to_append = text_to_append.replace('_', ' ')
            features.append(text_to_append)
    
    for col in has_columns:
        if property_dic[col] == True:
            text_to_append = f'Has {col}'
            text_to_append = text_to_append.replace('_', ' ')
            features.append(text_to_append)
    
    return ', '.join(features)

"""
Gets text representation for basement
"""
def get_basement_text(basement):
    if basement == 'Finished':
        return 'Has a finished basement'
    elif basement == 'No Basement':
        return 'Has no basement'
    
    return 'Has an unfinished basement'

"""
Create the metadata dictionary
"""
def create_metadata(mysql_id, property_dic):
    metadata = {
        "mysql_id": mysql_id,
        "property_type": property_dic['property_type'],
        "address": property_dic['address'],
        "num_beds": property_dic['number_of_beds'],
        "neighborhood": property_dic['neighborhood_type'],
        "city": property_dic['city'],
        "zipcode": property_dic['zipcode'],
        "latitude": property_dic['latitude'],
        "longitude": property_dic['longitude']
    }
    
    return metadata

"""
Checks to see if text only mentions a location (City or Place)

Returns true if the text only mentions a location
"""
def check_if_just_location(input_text):
    input_text = input_text.strip() 
    
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(input_text)
        
    entity_texts = [ent.text for ent in doc.ents]
    combined_entities = " ".join(entity_texts).strip()

    #Checks to see if words that aren't entities are used
    if len(input_text) != len(combined_entities):
        return False
    
    for ent in doc.ents:
        if ent.label_ != 'GPE':
            return False
        
    return True

"""
Searches Pinecone database, filtering only by location
"""
def search_by_location_only(search_query, index, top_k=100):
    search_query_embedding = embedding_model.encode([search_query])[0]

    results = index.query(
        vector = search_query_embedding.tolist(),  
        top_k = top_k,
        filter = {
            "city": {"$eq": search_query}
        },
        include_metadata = True
    )

    return results['matches']

"""
Gets city and zipcode from a given address
"""
def get_city_zip_from_address(address):
    split_address = address.split(',')
    
    city = split_address[1].strip()
    
    zipcode = None
    zipcode_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
    
    if zipcode_match:
        zipcode = zipcode_match.group(0)
        
    return city, zipcode
    
#df = pd.read_csv(r'API_Extraction\boston_properties.csv')
#example_uploader(df)

search_query = 'apartments Boston'
index = pc.Index('example-database')

if check_if_just_location(search_query) == True:
    print('yes')
    results = search_by_location_only(search_query, index)
    print(len(results))

