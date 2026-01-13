from fastapi import FastAPI
from app.models import RedactRequest, RedactResponse, PolicyRequest, PolicyResponse
from app.policy_store import load_policies
from app.retriever import RAGRetriever
from app.redactor import apply_redaction

app = FastAPI(title="Dynamic Policy Guard")


policies = load_policies()
retriever = RAGRetriever(policies)

@app.post("/redact", response_model=RedactResponse)
def redact(req: RedactRequest):
    query = " ".join([ent.type for ent in req.content.entities])

    retrieved_chunks = retriever.retrieve(
        customer_id=req.customer_id,
        query=query,
        version=req.policy_version,
        top_k=5
    )

    redacted_text, actions = apply_redaction(
        req.content.text,
        req.content.entities,
        retrieved_chunks
    )

    return RedactResponse(
        original_text_length=len(req.content.text),
        redacted_text=redacted_text,
        actions=actions
    )


from app.interpreter import interpret_policy_rag

@app.post("/policy/explain", response_model=PolicyResponse)
def policy(req: PolicyRequest):
    retrieved_chunks = retriever.retrieve(
        customer_id=req.customer_id,
        query=req.entity_type,
        version=req.policy_version,
        top_k=5
    )

    action, snippet = interpret_policy_rag(
        retrieved_chunks,
        req.entity_type
    )

    if not action:
        return PolicyResponse(
            applied_action="NONE",
            policy_source="",
            justification="No applicable policy found"
        )

    return PolicyResponse(
        applied_action=action,
        policy_source=snippet.split(" from ")[-1],
        justification=snippet
    )