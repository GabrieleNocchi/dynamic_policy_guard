import sys
from pathlib import Path

# aggiungi la root del progetto al path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# ora puoi importare i moduli
from app.retriever import RAGRetriever

# --- Chunk finti per test ---
fake_chunks = [
    {"text": "Keep NAME", "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},
    {"text": "REDACT EMAIL", "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},
    {"text": "MASK PHONE", "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},
    {"text": "GLOBAL rule applies", "metadata": {"DOCUMENT_ID": "POL-GLOBAL", "VERSION": "DEFAULT"}},
]

# --- Chunk finti basati sulle tue policy reali ---
fake_chunks = [
    # ACME V2
    {"text": "Le EMAIL devono essere convertite usando HASH per permettere analisi anonime.", 
     "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},
    {"text": "I numeri di PHONE devono essere parzialmente oscurati usando MASK_LAST_4 per verifica operatore.", 
     "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},
    {"text": "I NAME (nomi propri) sono considerati pubblici nel nostro caso, quindi KEEP.", 
     "metadata": {"CUSTOMER": "ACME", "VERSION": "V2"}},

    # BETA GEN
    {"text": "NAME applica REDACT", "metadata": {"CUSTOMER": "BETA", "VERSION": "GEN"}},
    {"text": "EMAIL applica REDACT", "metadata": {"CUSTOMER": "BETA", "VERSION": "GEN"}},
    {"text": "I numeri di PHONE che devono essere KEEP per esigenze di contatto urgenti.", 
     "metadata": {"CUSTOMER": "BETA", "VERSION": "GEN"}},

    # POL-GLOBAL
    {"text": "Se non viene trovata alcuna regola specifica per il cliente, applicare lo standard di sicurezza massimo: REDACT.", 
     "metadata": {"DOCUMENT_ID": "POL-GLOBAL", "VERSION": "DEFAULT"}},
    {"text": "Definizioni delle Azioni: REDACT, HASH, MASK_LAST_4, KEEP", 
     "metadata": {"DOCUMENT_ID": "POL-GLOBAL", "VERSION": "DEFAULT"}},
]

# --- Mock del retriever senza embeddings reali, ma con logica CUSTOMER+VERSION ---
class MockRetriever(RAGRetriever):
    def __init__(self):
        self.chunk_store = fake_chunks

    def retrieve(self, customer_id: str, query: str, version: str = None, top_k: int = 3):
        cust_upper = customer_id.upper() if customer_id else None
        version_upper = version.upper() if version else None

        # Filtra chunk per CUSTOMER+VERSION se version è valorizzato, altrimenti solo CUSTOMER
        if version_upper:
            filtered = [
                c for c in self.chunk_store
                if c["metadata"].get("CUSTOMER", "").upper() == cust_upper
                and c["metadata"].get("VERSION", "").upper() == version_upper
            ]
        else:
            filtered = [
                c for c in self.chunk_store
                if c["metadata"].get("CUSTOMER", "").upper() == cust_upper
            ]

        # fallback su POL-GLOBAL se nessuno trovato
        if not filtered:
            filtered = [
                c for c in self.chunk_store
                if c["metadata"].get("DOCUMENT_ID", "").upper() == "POL-GLOBAL"
            ]

        # match semplice sulla query (contiene testo)
        results = [c for c in filtered if query.upper() in c["text"].upper()]

        return results[:top_k]

# --- Test ACME ---
def test_acme_name():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="ACME", query="NAME", version="V2")
    assert len(results) == 1
    assert "NAME" in results[0]["text"]
    assert "KEEP" in results[0]["text"]

def test_acme_email():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="ACME", query="EMAIL", version="V2")
    assert len(results) == 1
    assert "EMAIL" in results[0]["text"]
    assert "HASH" in results[0]["text"]

def test_acme_phone():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="ACME", query="PHONE", version="V2")
    assert len(results) == 1
    assert "PHONE" in results[0]["text"]
    assert "MASK_LAST_4" in results[0]["text"]

# --- Test BETA ---
def test_beta_name():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="BETA", query="NAME", version="GEN")
    assert len(results) == 1
    assert "NAME" in results[0]["text"]
    assert "REDACT" in results[0]["text"]

def test_beta_email():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="BETA", query="EMAIL", version="GEN")
    assert len(results) == 1
    assert "EMAIL" in results[0]["text"]
    assert "REDACT" in results[0]["text"]

def test_beta_phone():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="BETA", query="PHONE", version="GEN")
    assert len(results) == 1
    assert "PHONE" in results[0]["text"]
    assert "KEEP" in results[0]["text"]

# --- Test fallback globale ---
def test_global_fallback():
    retriever = MockRetriever()
    results = retriever.retrieve(customer_id="UNKNOWN", query="REDACT")
    assert len(results) > 0
    assert "POL-GLOBAL" in results[0]["metadata"]["DOCUMENT_ID"]