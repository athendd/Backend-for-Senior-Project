from pinecone import Pinecone, ServerlessSpec
import pandas as pd
from category_encoders import BinaryEncoder
from sklearn.preprocessing import MinMaxScaler
import spacy
import openai
from sentence_transformers import SentenceTransformer
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

#Could switch to from sentence transformers to text-embedding-3-small to give more vectors
#item_0 is 1 that means they have the amenity

open_api_key = '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'
pinecone_api_key = 'pcsk_7V2pDe_2pxQsSG2KTR1YxgLP64PyYMfN6cWUVvWeMFHneFuPZNZiRnfQRjzfc36t8CkCJu'

embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

"""
Finds list of properties using semantic search
"""
def find_properties(search_query, top_k = 5):
    search_query_embedding = embedding_model.encode([search_query])[0]
    
    results = index.query(
        vector = search_query_embedding.tolist(),
        top_k = top_k,
        include_metadata = True
    )
    
    for match in results['matches']:
        print(match)

pc = Pinecone(api_key = pinecone_api_key, environment='example-environment')

#df = pd.read_csv(r'API_Extraction\boston_properties_dummy_data (1).csv')

index_name = 'example-database3'

#vector_dimension = 384

#similarity_metric = 'cosine'

"""
#Create the index
if index_name not in pc.list_indexes():
    pc.create_index(
        name = index_name,
        dimension = vector_dimension,
        metric = similarity_metric,
        spec = ServerlessSpec(cloud = 'aws', region = 'us-east-1')
    )
"""

index = pc.Index(index_name)

"""
first = df.iloc[0].to_dict()

combined_text = (
    f'{first['description']}. '
    f'Located at {first['address']}. '
    f'Neighborhood: {first['neighborhood_type']}. '
    f'Property: {first['property_type']}. '
)

#Normalization for numerical columns
scaler = MinMaxScaler()
numerical_cols = df.select_dtypes(include=['number']).columns
numerical_cols = numerical_cols.drop(['latitude', 'longitude', 'walk_score', 'bike_score', 'transit_score', 'year_built', 'min_occupants',
                                      'max_occupants', 'min_age', 'max_age', 'number_of_beds', 'number_of_baths'])
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

#Binary Encoding for boolean columns
binary_cols = ['washer', 'dryer', 'dishwasher', 'ac', 'heating', 'yard', 'pool',
               'balcony', 'office', 'utilities_included', 'handicap_accessible', 'fireplace', 'smoking_policy',
               'patio', 'ev_charging', 'hardwood_floors', 'fitness_center', 'recently_renovated', 'garage']
encoder = BinaryEncoder(cols = binary_cols)
df = encoder.fit_transform(df)

#Encoding for categorical columns
df = pd.get_dummies(df, columns = ['basement'])

for i, row in df.iterrows():
    original = row.to_dict()
    
    #Extract descriptive fields if available
    description = original.get('description', '')
    address = original.get('address', '')
    neighborhood = original.get('neighborhood_type', '')
    property_type = original.get('property_type', '')
    
    #Human-readable feature description
    features = []
    if original.get('washer_0', 1): features.append("has a washer")
    if original.get('dryer_0', 1): features.append("has a dryer")
    if original.get('garage_0', 1): features.append("includes a garage")
    if original.get('pool_0', 1): features.append("has a pool")
    if original.get('fitness_center_0', 1): features.append("includes fitness center")
    
    feature_summary = ', '.join(features)
        
    combined_text = (
        f"{description}. Located at {address}. "
        f"Neighborhood: {neighborhood}. Property type: {property_type}. "
        f"{feature_summary}"
    )

    embedding = embedding_model.encode([combined_text])[0]

    #Upload vector with metadata
    metadata = {
        "mysql_id": int(original.get("mysql_id", i)),
        "property_type": property_type,
        "address": address,
        "num_beds": original.get("number_of_beds", None),
        "neighborhood": neighborhood
    }

    index.upsert([
        {
            'id': str(original.get("mysql_id", i)),
            'values': embedding.tolist(),
            'metadata': metadata
        }
    ])
    
"""


user_query = "spacious home with at least 3 bedrooms and a garage in the city of Boston"

#find_properties(user_query, 5)


