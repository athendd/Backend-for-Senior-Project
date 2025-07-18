class PropertyVectorBuilder:
    def __init__(self, embedder):
        self.embedder = embedder

    def build(self, property_dic):
        text = self._combine_text(property_dic)
        return self.embedder.encode(text)

    def _combine_text(self, p):
        sections = [
            f"{p['description']}. Located in {p['city']}. {p['number_of_beds']}-bedroom, {p['number_of_baths']}-bath {p['property_type']}.",
            f"Has {p['number_of_floors']} floors. Rent: ${p['monthly_rent']}/month. Built in {p['year_built']}.",
            f"{p['neighborhood_type']} neighborhood. Occupants: {p['min_occupants']}-{p['max_occupants']}, Ages: {p['min_age']}-{p['max_age']}."
        ]

        sections.append(self._space_text(p['property_type'], p['square_footage']))
        sections.append("Is handicap accessible." if p['handicap_accessible'] else '')
        sections.append("Smoking is allowed." if p['smoking_policy'] else '')
        sections.append("Utilities included." if p['utilities_included'] else '')
        sections.append(self._basement_text(p['basement']))
        sections.append("Recently renovated." if p['recently_renovated'] else '')
        sections.append("Pets allowed." if p['pet_policy'] else '')

        boolean_cols = [
            'washer', 'dryer', 'ac', 'heating', 'garage', 'office', 'dishwasher',
            'yard', 'balcony', 'fireplace', 'patio', 'ev_charging',
            'hardwood_floors', 'fitness_center', 'pool'
        ]

        features = [col.replace('_', ' ') for col in boolean_cols if p.get(col)]
        if features:
            sections.append("Has: " + ", ".join(features) + '.')

        sections.append(self._score_text("Public transportation", p['transit_score']))
        sections.append(self._score_text("Biking", p['bike_score']))
        sections.append(self._score_text("Walking", p['walk_score']))

        return ' '.join([s for s in sections if s])

    def _space_text(self, property_type, sqft):
        if property_type == 'apartment':
            if sqft < 600: return 'Very little space.'
            elif sqft < 1000: return 'Average space.'
            return 'Spacious.'
        if sqft < 1000: return 'Very little space.'
        elif sqft < 2500: return 'Average space.'
        return 'Spacious.'

    def _basement_text(self, basement):
        if basement == 'Finished': return 'Finished basement.'
        if basement == 'Unfinished': return 'Unfinished basement.'
        return ''

    def _score_text(self, category, score):
        if score < 21: return f"{category} is very limited."
        elif score < 41: return f"{category} available but not convenient."
        elif score < 61: return f"Fair {category.lower()} support."
        elif score < 81: return f"Reliable {category.lower()} access."
        return f"Excellent {category.lower()} access."
