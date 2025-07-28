from rapidfuzz import process, fuzz

class MisspellerFixer:
    def __init__(self, keywords):
        self.keywords = [k.lower() for k in keywords]

    def correct_single_misspell(self, candidate, score_cutoff=75):
        match = process.extractOne(candidate.lower(), self.keywords, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
        return self.capitalize_name(match[0]) if match else None

    def correct_text(self, text, max_length):
        tokens = text.split()
        n = len(tokens)
        corrected = []
        i = 0

        while i < n:
            matched = False
            for size in range(max_length, 0, -1):  
                if i + size > n:
                    continue
                window = tokens[i:i + size]
                window_text = ' '.join(window)
                corrected_token = self.correct_single_misspell(window_text)
                if corrected_token:
                    corrected.append(corrected_token)
                    i += size  
                    matched = True
                    break
            if not matched:
                corrected.append(tokens[i])
                i += 1

        return ' '.join(corrected)

    def capitalize_name(self, name):
        return ' '.join(w.capitalize() for w in name.split())