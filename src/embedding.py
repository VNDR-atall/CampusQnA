import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    _instance = None
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model_name = model_name
        self.model = None
    
    def _load_model(self):
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Embedding model loaded successfully")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        self._load_model()
        embeddings = self.model.encode(texts)
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        self._load_model()
        embedding = self.model.encode(text)
        return embedding
    
    @classmethod
    def get_instance(cls, model_name: str = "BAAI/bge-small-zh-v1.5") -> "EmbeddingModel":
        if cls._instance is None:
            cls._instance = EmbeddingModel(model_name)
        return cls._instance