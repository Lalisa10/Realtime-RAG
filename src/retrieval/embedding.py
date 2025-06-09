from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
    
    def generate(self, text):
        return self.model.encode(text, convert_to_tensor=False).tolist()