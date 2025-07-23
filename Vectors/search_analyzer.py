from nltk.tokenize import word_tokenize

class SearchAnalyzer:
    def __init__(self):
        self.KEYWORD_MAPPING = {
            'bedroom': 'num_beds', 'bed': 'num_beds', 'bedrooms': 'num_beds',
            'bath': 'num_baths', 'bathroom': 'num_baths',
            'washer': 'washer', 'dryer': 'dryer',
            'yard': 'yard', 'basement': 'basement', 'ac': 'ac',
            'garage': 'garage', 'pool': 'pool', 'renovated': 'recently_renovated'
        }

    def update_filters_dict(self, search_query, advanced_filters, location):    

        #Remove location string from query to avoid misinterpreting it as a keyword
        cleaned_query = search_query.replace(location, '').lower()
        words = word_tokenize(cleaned_query)

        #Add keyword-based filters only if not already set
        for i, word in enumerate(words):
            for kword, field in self.KEYWORD_MAPPING.items():
                if kword in word:
                    if advanced_filters.get(field) is None:  
                        if i > 0 and words[i - 1].isdigit():
                            advanced_filters[field] = int(words[i - 1])
                        else:
                            advanced_filters[field] = True

        return advanced_filters