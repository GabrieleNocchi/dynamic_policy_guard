from typing import List
from app.actions import ACTION_MAP
from app.models import Entity, ActionResult
from app.interpreter import interpret_policy_rag

def apply_redaction(text: str, entities: List[Entity], retrieved_chunks):
    offset = 0
    actions = []

    for ent in entities:
        action, snippet = interpret_policy_rag(retrieved_chunks, ent.type)
        if not action:
            continue
        func = ACTION_MAP[action]
        transformed = func(ent.value)

        start = ent.start + offset
        end = ent.end + offset
        text = text[:start] + transformed + text[end:]
        offset += len(transformed) - (end - start)

        actions.append(
            ActionResult(
                entity_type=ent.type,
                original_value=ent.value,
                applied_action=action,
                policy_source=snippet.split(" from ")[-1],
                justification=snippet
            )
        )

    return text, actions

