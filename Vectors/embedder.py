from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text):
        return self.model.encode([text])[0].tolist()