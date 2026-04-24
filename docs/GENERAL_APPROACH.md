# General Approach — Non-Compromisables

## Objectives

- **Maximize the grade.** Every graded criterion must be explicitly satisfied. Bonus marks are attempted where cheap to add.
- **No hardcoded or demo inputs.** The startup idea is passed at runtime (CLI arg or prompt). No agent output is faked or pre-written. All LLM calls are live.
- **Easiest technical route.** Use CrewAI for agent definition and task orchestration. Use a shared Python dictionary as the message bus. No Redis, no SQLite, no separate processes unless required.
- **Everything must be demo-ready.** The full pipeline runs end-to-end from a single `python main.py` invocation. All platform actions (GitHub PR, Slack message, email) must be visible and verifiable by the evaluator.

## Stack Decisions

| Concern | Decision |
|---|---|
| Agent framework | CrewAI |
| LLM provider | Anthropic Claude (all agents, single API key) |
| Message bus | Shared Python `dict` in `message_bus.py` |
| GitHub integration | Direct `requests` calls to `api.github.com` |
| Slack integration | `requests` to `chat.postMessage`, Block Kit formatting |
| Email | SendGrid Python SDK |
| Secrets | `.env` file loaded via `python-dotenv`, never committed |

## Message Schema (enforced on every inter-agent message)

```json
{
  "message_id": "<uuid>",
  "from_agent": "<agent_name>",
  "to_agent": "<agent_name>",
  "message_type": "task | result | revision_request | confirmation",
  "payload": {},
  "timestamp": "<ISO 8601>",
  "parent_message_id": "<uuid | null>"
}
```

## Feedback Loop Requirement

The CEO agent must perform LLM-based review of at least one sub-agent output and issue a `revision_request` if the output is insufficient. This is the single hardest graded criterion — it must work reliably in the demo.

## File Layout

```
launchmind-grayhat/
├── agents/
│   ├── ceo_agent.py
│   ├── product_agent.py
│   ├── engineer_agent.py
│   ├── marketing_agent.py
│   └── qa_agent.py
├── message_bus.py
├── main.py
├── requirements.txt
├── .env              ← never committed
├── .env.example
├── .gitignore
└── README.md
```
