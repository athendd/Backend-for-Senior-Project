from walkscore import WalkScoreAPI

walk_score_api_key = 'WALK_SCORE_API_KEY'

class WalkScoreExtractor():
    
    def __init__(self):
        self.walkscore_api = WalkScoreAPI(api_key = walk_score_api_key)
        
    def get_scores(self, lat, lon, address):
        try:
            scores = {}
            result = self.walkscore_api.get_score(latitude=lat,
                                              longitude=lon, 
                                              address = address, 
                                              return_bike_score=True,
                                              return_transit_score=True)
            scores['walk_score'] = result.walk_score
            scores['bike_score'] = result.bike_score
            scores['transit_score'] = result.transit_score
        except Exception as e:
            print(f"An error occurred when connecting to walk score api: {e}")
            return None

        return scores
            

