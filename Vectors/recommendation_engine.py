from pinecone_interactor import PineconeInteractor

class RecommendationEngine():
    
    def __init__(self, pinecone_interactor: PineconeInteractor, top_k = 5):
        self.pinecone_interactor = pinecone_interactor
        self.top_k = top_k
        
    def recommendation_pipeline(self, user_dict):
        user_recommendations_dict = {}
        for user in user_dict.keys():
            if len(user_dict[user]) >= 3:
                mysql_ids, places = user_dict[user]
                user_recommendations_dict[user] = self.recommended_properties(mysql_ids, places)
            else:
                user_recommendations_dict[user] = []
            
    
    def recommended_properties(self, favorite_properties_ids, places):
        if favorite_properties_ids == []:
            return []
        
        seen = set()
        recommendations_list = []
        
        for i in range(len(favorite_properties_ids)):
            filter_dict = {'city': places[i]}
            recommendations = self._property_recommendations(favorite_properties_ids[i], filter_dict)
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