# Module 02 — CEO Agent

## Goal

Receive startup idea at runtime, orchestrate all sub-agents, perform LLM-based review, run at least one feedback loop, post final Slack summary.

## File

`agents/ceo_agent.py`

## Inputs

- `idea: str` — passed from `main.py`, sourced from CLI arg or `input()`. Never hardcoded.

## LLM Calls (minimum 2, required by spec)

### Call 1 — Task Decomposition

**System prompt:** You are the CEO of an AI-powered startup studio. Given a startup idea, produce a structured JSON task list: one task for the Product agent, one for the Engineer agent, one for the Marketing agent. Each task must include `agent`, `focus`, and `context` fields. Return only valid JSON.

**User prompt:** `idea`

**Output:** Dict with keys `product_task`, `engineer_task`, `marketing_task`.

### Call 2 — Output Review

**System prompt:** You are a critical startup CEO reviewing agent deliverables. Given a product specification JSON, evaluate whether it is specific and complete. Return JSON with fields: `verdict` ("pass" or "fail"), `reason` (one sentence), `feedback` (specific instructions for revision if fail, else null).

**User prompt:** Serialised product spec from Product agent.

**Output:** `{ verdict, reason, feedback }`

## Flow

```
1. Receive idea
2. LLM Call 1 → task messages
3. send(ceo → product, task)
4. send(ceo → engineer, task)
5. send(ceo → marketing, task)
6. Run ProductAgent → receive result
7. LLM Call 2 → review product spec
8.   If fail → send(ceo → product, revision_request) → re-run ProductAgent → receive revised result
9. Run EngineerAgent (pass product spec) → receive result (PR URL, issue URL)
10. Run MarketingAgent (pass product spec + PR URL) → receive result
11. Run QAAgent (pass HTML + marketing copy + PR URL) → receive review report
12.   If QA fail → send(ceo → engineer, revision_request) → re-run EngineerAgent
13. Compile final summary
14. Post final Slack message (Block Kit) to SLACK_CHANNEL
15. Print full message log
```

## Outputs

- Structured task messages (via message bus) to each sub-agent
- `revision_request` messages when review fails
- Final Slack message summarising PR URL, product tagline, and QA verdict
- Full message log printed to terminal

## Constraints

- CEO never skips the review step.
- At least one `revision_request` must be demonstrable. If the LLM returns "pass" on first review, the demo may look like a fixed pipeline — test with a deliberately thin idea to trigger a fail.
