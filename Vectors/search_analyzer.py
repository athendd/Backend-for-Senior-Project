from nltk.tokenize import word_tokenize

class SearchAnalyzer:
    def __init__(self):
        self.KEYWORD_MAPPING = {
            'bedroom': 'num_beds', 'bed': 'num_beds', 'bedrooms': 'num_beds', 'beds': 'num_beds', 
            'bath': 'num_baths', 'bathroom': 'num_baths', 'bathrooms': 'num_baths', 'baths': 'num_baths',
            'washer': 'washer', 'dryer': 'dryer',
            'yard': 'yard', 'basement': 'basement', 'ac': 'ac', 'central air': 'ac', 
            'garage': 'garage', 'pool': 'pool', 'renovated': 'recently_renovated',
            'recently renovated': 'recently_renovated', 'apartment': 'property_type', 'condo': 'property_type',
            'house': 'property_type', 'duplex': 'property_type', 'studio': 'property_type', 'houses': 'property_type',
            'apartments': 'property_type', 'studios': 'property_type', 'condos': 'property_type', 'duplexes': 'property_type',
            'suburban': 'neighborhood_type', 'urban': 'neighborhood_type', 'rural': 'neighborhood_type'
        }

    def update_filters_dict(self, search_query, advanced_filters, location):    
        words_to_check = ['pool', 'renovated', 'garage', 'ac', 'basement', 'yard', 'washer', 'dryer']
        words_to_select = ['property_type', 'neighborhood_type']

        #Remove location string from query to avoid misinterpreting it as a keyword
        cleaned_query = search_query.replace(location, '').lower()
        words = word_tokenize(cleaned_query)

        #Add keyword-based filters only if not already set
        for i, word in enumerate(words):
            for kword, field in self.KEYWORD_MAPPING.items():
                if kword in word:
                    if advanced_filters.get(field) is None:  
                        if field in words_to_check:
                            advanced_filters[field] = True
                        elif field in words_to_select:
                            if words[i].endswith('s'):
                                advanced_filters[field] = words[i][:-1].capitalize()
                            else:
                                advanced_filters[field] = words[i].capitalize()
                        else:
                            if i > 0 and words[i - 1].isdigit():
                                advanced_filters[field] = {'$gte': int(words[i - 1])}

        return advanced_filters