from rapidfuzz import process, fuzz

class PlaceMisspeller:
    def __init__(self, places):
        self.places = [p.lower() for p in places]

    def place_exists(self, place):
        return place.lower() in self.places

    def correct_place(self, canidate, score_cutoff= 10):
        match = process.extractOne(canidate, self.places, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
        if match != None:
            return self.capitalize_name(match[0])
        
        return None

    def get_place_candidates(self, text):
        tokens = text.lower().split()
        candidates = []
        for i in range(len(tokens)):
            for j in range(i + 1, min(i + 4, len(tokens) + 1)):
                phrase = ' '.join(tokens[i:j])
                candidates.append(phrase)
                
        return candidates
    
    def get_best_match(self, canidate, score_cutoff=10):
        return process.extractOne(canidate.lower(), self.places, scorer=fuzz.WRatio, score_cutoff=score_cutoff)


    def capitalize_name(self, name):
        return ' '.join(w.capitalize() for w in name.split())