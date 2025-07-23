from rapidfuzz import process, fuzz

class MisspellerFixer:
    def __init__(self, keywords):
        self.keywords = [k.lower() for k in keywords]

    def correct_single_misspell(self, candidate, score_cutoff=10):
        match = process.extractOne(candidate.lower(), self.keywords, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
        return self.capitalize_name(match[0]) if match else None

    def correct_text(self, text):
        tokens = text.split()
        corrected = []
        for token in tokens:
            corrected_token = self.correct_single_misspell(token)
            corrected.append(corrected_token if corrected_token else token)
        return ' '.join(corrected)

    def capitalize_name(self, name):
        return ' '.join(w.capitalize() for w in name.split())