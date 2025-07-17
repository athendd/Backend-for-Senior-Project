from pinecone_interactor import PineconeInteractor

class RecommendationEngine():
    
    def __init__(self, favorite_properties_ids):
        self.favorite_properties_ids = favorite_properties_ids
        self.pinecone_interactor = PineconeInteractor('new-example-database')  
    
    def get_recommended_properties(self):
        if self.favorite_properties_ids == []:
            return []

        recommendation_list = []
        for favorite_property_id in self.favorite_properties_ids:
            recommendations = self.property_recommendations(favorite_property_id)
            if recommendations != []:
                recommendation_list = self.check_for_duplicates(recommendation_list, recommendations)
                            
        return recommendation_list
            
    def property_recommendations(self, favorite_property_id):
        property_vector = self.pinecone_interactor.get_vector(favorite_property_id)
        if property_vector == None:
            return []
        
        return self.pinecone_interactor.perform_search(property_vector, 5, None)
    
    def check_for_duplicates(self, recommendation_list, recommendations):
        for recommendation in recommendations:
            if recommendation not in recommendation_list:
                recommendation_list.append(recommendation)
                
        return recommendation_list            