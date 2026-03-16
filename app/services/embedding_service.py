from typing import List
from sentence_transformers import SentenceTransformer
MODEL_NAME="all-MiniLM-L6-v2"
_model=SentenceTransformer(MODEL_NAME)
def embed_text(text:str)->List[float]:
    vector=_model.encode(text)
    return vector.tolist()
def embed_texts(text:str)->List[str]:
    vectors=_model.encode(text)
    return [vector_text.tolist() for vector_text in vectors]
