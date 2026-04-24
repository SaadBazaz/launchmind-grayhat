# Module 03 — Product Agent

## Goal

Receive task from CEO, produce a complete structured product spec via LLM, send to Engineer and Marketing agents, confirm back to CEO.

## File

`agents/product_agent.py`

## Inputs

- Task message from CEO (via message bus): `{ idea, focus, context }`

## LLM Call

**System prompt:** You are an experienced product manager. Given a startup idea and focus areas, produce a detailed product specification as valid JSON matching the exact schema below. Be specific — generic outputs will be rejected.

**Schema to produce:**
```json
{
  "value_proposition": "string",
  "personas": [
    { "name": "string", "role": "string", "pain_point": "string" }
  ],
  "features": [
    { "name": "string", "description": "string", "priority": 1 }
  ],
  "user_stories": [
    { "as_a": "string", "i_want": "string", "so_that": "string" }
  ]
}
```

**Requirements:** 2–3 personas, exactly 5 features ranked 1–5, exactly 3 user stories.

**User prompt:** Serialised task payload.

## Flow

```
1. receive_latest("product") from message bus
2. Extract idea + focus from payload
3. LLM Call → product spec JSON
4. send(product → engineer, result, payload=spec)
5. send(product → marketing, result, payload=spec)
6. send(product → ceo, confirmation, payload={ "status": "ready", "spec": spec })
```

## Revision Handling

If a `revision_request` message arrives from CEO:
- Extract `feedback` field from payload
- Append feedback to user prompt: "Your previous output was rejected. Feedback: {feedback}. Revise accordingly."
- Re-run LLM call
- Re-send results to engineer, marketing, ceo

## Outputs

- Product spec JSON → engineer (message bus)
- Product spec JSON → marketing (message bus)
- Confirmation → CEO (message bus)
