from pathlib import Path
from typing import List, Dict
from app.actions import ACTION_MAP

ACTIONS = list(ACTION_MAP.keys())

class PolicyDocument:
    def __init__(self, text: str, metadata: Dict[str, str], filename: str):
        self.text = text
        self.metadata = metadata
        self.filename = filename  

def load_policies(path: str = "policies") -> List[PolicyDocument]:
    documents = []

    for file in Path(path).glob("*.txt"):
        raw = file.read_text(encoding="utf-8")

        # estrai metadata dal filename
        doc_name = file.stem  
        parts = doc_name.split("-")
        customer = parts[1] if len(parts) > 1 else ""
        version = parts[2] if len(parts) > 2 else ""
        metadata = {
            "DOCUMENT_ID": doc_name,
            "CUSTOMER": customer,
            "VERSION": version
        }

        # tutto il resto del testo
        body_lines = raw.splitlines()

        # rimuovi linee che contengono un'azione della mappa seguita da ":" (la definizione delle azione dentro POL-GLOBAL)
        filtered_lines = [
            line for line in body_lines
            if not any(f"{action}:" in line.upper() for action in ACTIONS)
        ]

        text = "\n".join(filtered_lines).strip()

        documents.append(
            PolicyDocument(
                text=text,
                metadata=metadata,
                filename=file.name
            )
        )

    return documents
