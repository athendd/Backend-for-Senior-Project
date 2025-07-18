from pinecone_interactor import PineconeInteractor

class RecommendationEngine():
    
    def __init__(self, favorite_properties_ids, pinecone_interactor: PineconeInteractor, top_k = 50):
        self.favorite_properties_ids = favorite_properties_ids
        self.pinecone_interactor = pinecone_interactor
        self.top_k = top_k
    
    def recommended_properties(self, filter_dict = None):
        if self.favorite_properties_ids == []:
            return []
        
        seen = set()
        recommendations_list = []
        
        for favorite_property_id in self.favorite_properties_ids:
            recommendations = self._property_recommendations(favorite_property_id, filter_dict)
            for recommendation in recommendations:
                if recommendation not in seen and recommendation not in self.favorite_properties_ids:
                    seen.add(recommendation)
                    recommendations_list.append(recommendation)
              
        return recommendations_list
            
    def _property_recommendations(self, favorite_property_id, filter_dict):
        property_vector = self.pinecone_interactor.get_vector(favorite_property_id)
        if property_vector == None:
            return []
        
        return self.pinecone_interactor.perform_search(property_vector, self.top_k, filter_dict) 