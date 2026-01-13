from typing import Tuple, List
from app.actions import ACTION_MAP

ENTITY_LIST = ["NAME", "PHONE", "EMAIL"]

def interpret_policy_rag(retrieved_chunks: List[Tuple[str, dict]], entity_type: str) -> Tuple[str, str]:
    entity_upper = entity_type.upper()
    other_entities = set(e for e in ENTITY_LIST if e != entity_upper)

    # Chunk specifici (entità + azione)
    for chunk, meta in retrieved_chunks:
        chunk_upper = chunk.upper()
        for action in ACTION_MAP.keys():
            if entity_upper in chunk_upper and action in chunk_upper:
                return action, f"Matched snippet: '{chunk}' from {meta.get('DOCUMENT_ID')}"

    # Chunk generici (azione presente, ma nessun’altra entità)
    for chunk, meta in retrieved_chunks:
        chunk_upper = chunk.upper()
        for action in ACTION_MAP.keys():
            if action in chunk_upper and not any(e in chunk_upper for e in other_entities):
                return action, f"Matched generic snippet: '{chunk}' from {meta.get('DOCUMENT_ID')}"

    return None, "No matching rule found"
