import random
    
def get_scores():
    scores = {}
    scores['walk_score'] = generate_number(0, 100)
    scores['bike_score'] = generate_number(0, 100)
    scores['transit_score'] = generate_number(0, 100)
    
    return scores

def generate_number(start, end):
    return random.randint(start, end)