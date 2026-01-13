from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: List[str]) -> np.ndarray:
    return model.encode(chunks, convert_to_numpy=True)
