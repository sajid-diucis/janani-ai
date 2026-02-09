"""
Embeddings Service - Simple fallback without sentence-transformers
"""
from typing import List, Union
import hashlib
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.dimension = 768  # Match ChromaDB default
        
    def embed_text(self, text: str) -> List[float]:
        '''Single text embedding - 768 dimensions'''
        hash_obj = hashlib.sha384(text.encode())
        hash_bytes = hash_obj.digest()
        arr = np.frombuffer(hash_bytes, dtype=np.uint8).astype(float)
        arr = arr / 255.0
        # Expand to 768 dimensions by repeating
        arr = np.tile(arr, 16)  # 48 * 16 = 768
        return arr.tolist()
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        '''Batch encoding'''
        if isinstance(texts, str):
            texts = [texts]
        return np.array([self.embed_text(t) for t in texts])

embedding_service = EmbeddingService()
