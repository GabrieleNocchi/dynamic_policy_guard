import numpy as np
from typing import List, Tuple
from app.policy_store import PolicyDocument
from app.embeddings import embed_chunks
import re

from app.actions import ACTION_MAP

ACTIONS = list(ACTION_MAP.keys())
class RAGRetriever:
    def __init__(self, policies: List):
        # salva tutti i chunk con metadata
        self.chunk_store = []  

        action_pattern = re.compile(r'\b(' + '|'.join(ACTIONS) + r')\b|(\.)', flags=re.IGNORECASE)

        for policy in policies:
            text = policy.text
            filename = policy.filename  # usiamo il filename

            # estrai metadata dal filename
            doc_name = filename.split(".")[0]          
            parts = doc_name.split("-")
            customer = parts[1] if len(parts) > 1 else ""
            version = parts[2] if len(parts) > 2 else ""

            metadata = {
                "DOCUMENT_ID": doc_name,
                "CUSTOMER": customer,
                "VERSION": version
            }

            # chunking basato sulle azioni
            start = 0
            for match in action_pattern.finditer(text):
                end = match.end()
                chunk_text = text[start:end].strip()
                if chunk_text:
                    self.chunk_store.append({"text": chunk_text, "metadata": metadata})
                start = end

            # eventuale testo rimanente
            if start < len(text):
                remaining = text[start:].strip()
                if remaining:
                    self.chunk_store.append({"text": remaining, "metadata": metadata})
                    
                    

    def retrieve(self, customer_id: str, query: str, version: str = None, top_k: int = 3) -> List[Tuple[str, dict]]:
        cust_upper = customer_id.upper() if customer_id else None
        version_upper = version.upper() if version else None

        # Filtra chunk per CUSTOMER+VERSION se version_upper è valorizzato, altrimenti solo CUSTOMER
        if version_upper:
            filtered_chunks = [
                c for c in self.chunk_store
                if c["metadata"].get("CUSTOMER", "").upper() == cust_upper
                and c["metadata"].get("VERSION", "").upper() == version_upper
            ]
        else:
            filtered_chunks = [
                c for c in self.chunk_store
                if c["metadata"].get("CUSTOMER", "").upper() == cust_upper
            ]

        # Se non ci sono chunk specifici, usa POL-GLOBAL
        if not filtered_chunks:
            filtered_chunks = [
                c for c in self.chunk_store
                if c["metadata"].get("DOCUMENT_ID", "").upper() == "POL-GLOBAL"
            ]

        if not filtered_chunks:
            return []

        # Embedding solo sui chunk filtrati
        chunk_texts = [c["text"] for c in filtered_chunks]
        chunk_embeddings = embed_chunks(chunk_texts)
        query_emb = embed_chunks([query])[0]

        # Similarità coseno
        scores = np.dot(chunk_embeddings, query_emb) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_emb)
        )
        idx = np.argsort(-scores)[:top_k]
        return [(chunk_texts[i], filtered_chunks[i]["metadata"]) for i in idx]
