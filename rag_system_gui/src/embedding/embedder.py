from sentence_transformers import SentenceTransformer
from rag_system_gui.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
    
    def generate_embeddings(self, texts):
        return self.model.encode(texts)