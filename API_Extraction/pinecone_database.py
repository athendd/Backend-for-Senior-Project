from pinecone import Pinecone, ServerlessSpec
import logging
import openai
import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re

pinecone_api_key = 'pcsk_7V2pDe_2pxQsSG2KTR1YxgLP64PyYMfN6cWUVvWeMFHneFuPZNZiRnfQRjzfc36t8CkCJu'
pc = Pinecone(api_key = pinecone_api_key, environment='example-environment')
openai_api_key = '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'

"""
Uploader for example database
"""
def example_uploader(df):
    for i, row in df.iterrows():
        original = row.to_dict()
        
        

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
"""
def upload_property_vectory(index_name, property_dic, mysql_id):
    combined_text = create_text(property_dic)
    combined_text += get_text_representations(property_dic)
    
    city, zipcode = get_city_zip_from_address(property_dic['address'])
    
    property_dic['city'] = city
    property_dic['zipcode'] = zipcode 
    
    metadata = create_metadata(mysql_id, property_dic)
    
    index = pc.Index(index_name)
    
"""
OpenAI perform text embedding on combined text
"""
def get_openai_embedding(text):
    response = openai.embeddings.create(model = 'text-embedding-3-small', input = [text])
    
    return response.data[0].embedding

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
    
    if property_dic['utilities'] == True:
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
        "neighborhood": property_dic['neighborhood_type']
    }
    
    return metadata

"""
Checks to see if text just mentions a location 
"""
def check_if_just_location(input_text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(input_text)
    
    for ent in doc.ents:
        if ent.label_ != 'GPE' and ent.label_ != 'LOC':
            return False
        
    return True

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
    


    
    
